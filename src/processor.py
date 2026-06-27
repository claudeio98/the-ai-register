import os
import json
import re
import sqlite3
from datetime import datetime
from urllib.parse import urlparse
from db import get_connection
from dedup import compute_fingerprint, find_canonical, _resolve_canonical, get_duplicate_count, semantic_check
from llm import get_client

SYSTEM_PROMPT = """
You are an AI Events Intelligence agent. Your task is to extract high-value ML/AI talks and conferences from the provided raw text.

For each event found, extract:
- title: The name of the event.
- speaker: The main speaker (if any).
- institution: The organization hosting or the speaker's affiliation.
- date: The date of the event (ISO format if possible). This field is REQUIRED — find any date reference on the page. Look in headings, body text, sidebar, registration info. If the page mentions a date range, use the start date. ALWAYS include a date if one exists on the page. Only leave it empty if there is genuinely no date reference anywhere.
- url: The specific URL for the event (if available, otherwise use the page URL).
- location: The physical venue, city, or "Online" for virtual events. Look for location info in the page content, venue name, or city name.
- score: A score from 0 to 10 based on the criteria below.
- reasoning: A short explanation for the score.

Scoring criteria (0-10 scale):
- +4 to +6: Event hosted or co-hosted by a top-tier AI lab (DeepMind, OpenAI, Meta AI, Google Research, Anthropic, Microsoft Research) OR a top-tier university (Imperial, UCL, KCL, Oxford, Cambridge, MIT, Stanford). Recognized keynote speakers from these orgs push toward the higher end.
- +3 to +5: Event organized by a recognized conference organizer (e.g., AI Accelerator Institute, Gartner) OR featuring world-renowned academics or industry leaders as speakers.
- +2 to +3: Event highly relevant to ML/AI business or academic breakthroughs, OR featuring multiple reputable speakers from notable companies (e.g., Hugging Face, Synthesia, Wayve, Luma AI, Stability AI).
- +1: Moderately relevant AI/ML event with reasonable quality but no big names.
- -2 to -4: Low-quality, generic non-AI marketing, or events clearly irrelevant to ML/AI.

IMPORTANT RULES - Read carefully:
1. Do NOT extract individual workshops, talks, or sessions from a conference/workshop agenda or schedule page. Extract only the main conference or workshop event itself. A single page should produce at most ONE event entry.
2. For dates: If you see a month+day (e.g., "April 27") without an explicit year, infer the year from the page URL, page title, or visible year in the heading. NEVER guess the next year. Look for year hints in URLs (e.g., `/2026/` means the year is 2026), page titles (e.g., "ICLR 2026" means 2026), and surrounding context.
3. Return valid JSON only.

IMPORTANT - Conference pages: If the page is a conference/event registration page, agenda, or overview, do NOT penalize it for containing marketing/registration copy. Instead, evaluate it based on the organizer's reputation, speakers, and agenda quality. A conference with recognized organizers and high-quality speakers should score well even if the page is primarily promotional.

Example: The "Generative AI Summit | London" organized by AI Accelerator Institute features speakers from OpenAI, Meta, Hugging Face, and Wayve. Despite being a registration page, this should score 5-7 based on organizer quality and speaker roster — NOT penalized for being a registration page.

Return the results as a JSON object with a key "events" containing a list of these objects. If no events are found, return {"events": []}.
"""


def backfill_sources_from_events(events, parent_source_id):
    """
    After extracting events from a page, save any event URLs that aren't
    already in the sources table as new discovered sources.
    Backfilled sources have last_checked=NULL so they're fetched next run.
    Returns the number of new sources created.
    """
    if not events:
        return 0

    count = 0
    with get_connection() as conn:
        cursor = conn.cursor()
        for event in events:
            event_url = event.get("url", "").strip()
            if not event_url:
                continue
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO sources (url, description, category, parent_id) "
                    "VALUES (?, ?, ?, ?)",
                    (event_url,
                     f"Backfilled from processor on source {parent_source_id}",
                     "discovered",
                     parent_source_id)
                )
                if cursor.rowcount > 0:
                    count += 1
            except sqlite3.Error as e:
                print(f"Error backfilling source {event_url}: {e}")
        conn.commit()
    return count


def validate_event_date(event, page_url):
    """
    Validate and fix the year on an extracted event by cross-referencing
    against year hints in the URL (both event URL and page URL).

    Common bug: LLM sees "April 27" without a year and guesses the wrong
    year (e.g. 2027 instead of 2026). URL paths often contain the correct year.

    Also attempts to extract a date from URL path segments if the LLM
    returned no date but the URL has a date pattern like /2026/04/15/.

    Returns the corrected date string (or original if no fix needed).
    """
    date_str = event.get("date", "")
    event_url = event.get("url", page_url) or page_url
    urls_to_check = [page_url]
    if event_url != page_url:
        urls_to_check.append(event_url)

    # If no date was extracted, try to find one in the URL path
    if not date_str:
        for u in urls_to_check:
            try:
                parsed = urlparse(u)
                # Match /YYYY/MM/DD in path
                m = re.search(r'/(20\d{2})/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])', parsed.path)
                if m:
                    date_str = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
                    print(f"  [date from URL] \"{event.get('title', '')}\": {date_str}")
                    break
            except Exception:
                pass
        if not date_str:
            return date_str

    # Try to parse a YYYY or YYYY-MM-DD date
    match = re.match(r'^(\d{4})(?:-\d{2}(?:-\d{2})?)?$', date_str)
    if not match:
        return date_str

    extracted_year = int(match.group(1))

    # Collect year hints from both URLs
    url_years = set()
    for u in urls_to_check:
        try:
            parsed = urlparse(u)
            for y in re.findall(r'/20(\d{2})(?:/|$)', parsed.path):
                url_years.add(2000 + int(y))
            for y in re.findall(r'20(\d{2})', parsed.netloc):
                url_years.add(2000 + int(y))
        except Exception:
            pass

    if url_years and extracted_year not in url_years:
        corrected_year = min(url_years, key=lambda y: abs(y - extracted_year))
        corrected = date_str.replace(str(extracted_year), str(corrected_year), 1)
        print(f"  [date fix] \"{event.get('title', '')}\": year {extracted_year} -> {corrected_year} "
              f"(URL hints: {url_years})")
        return corrected

    return date_str


def _is_future_date(date_str: str | None, today: datetime) -> bool:
    """Check if a date string represents today or a future date.

    Handles multiple formats stored in the DB: YYYY, YYYY-MM, YYYY-MM-DD.
    Events with no date are included (we can't rule them out).
    """
    if not date_str:
        return True
    parts = date_str.split("-")
    if len(parts) == 1 and len(parts[0]) == 4:
        return int(parts[0]) >= today.year
    if len(parts) == 2:
        return (int(parts[0]), int(parts[1])) >= (today.year, today.month)
    if len(parts) == 3:
        return date_str >= today.strftime("%Y-%m-%d")
    return True


def process_page(page_id, url, content, source_id):
    """
    Process a page: extract events via LLM, insert them with provenance,
    and backfill any new source URLs found.
    Returns the list of extracted events (or empty list).
    """
    print(f"Processing page {page_id}: {url}")
    try:
        response = get_client().chat.completions.create(
            model=os.environ.get("MODEL_NAME", "deepseek/deepseek-v4-flash"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"URL: {url}\n\nContent:\n{content}"}
            ],
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)
        events = data.get("events", [])

        if not events:
            return []

        with get_connection() as conn:
            cursor = conn.cursor()
            for event in events:
                try:
                    event_url = event.get("url", url) or url
                    event_title = event.get("title", "")
                    event_date = validate_event_date(event, url)
                    event_score = event.get("score", 0) or 0

                    # Skip past events — they already happened
                    if not _is_future_date(event_date, datetime.now()):
                        print(f"  Skipping past event: \"{event_title[:60]}\" (date={event_date})")
                        continue

                    # Phase 1 & 2: Fingerprint and Fuzzy match
                    canonical_id, match_type, flag = find_canonical(
                        cursor, event_title, event_date, event_url, float(event_score)
                    )

                    # Phase 3: Semantic match (LLM) if no match found
                    if not canonical_id and event_title and event_date:
                        cursor.execute(
                            "SELECT id, title, date, url, score, created_at FROM events "
                            "WHERE date = ? AND canonical_event_id IS NULL",
                            (event_date,)
                        )
                        candidates = cursor.fetchall()

                        incoming_words = set(event_title.lower().split())

                        for cand in candidates:
                            cand_id, cand_title, cand_date, cand_url, cand_score, cand_created = cand
                            cand_words = set(cand_title.lower().split())
                            common_words = incoming_words & cand_words
                            if len(common_words) < 2:
                                continue

                            cand_event = {
                                "title": cand_title, "date": cand_date, "url": cand_url
                            }
                            incoming_event = {
                                "title": event_title, "date": event_date, "url": event_url
                            }

                            print(f"  [LLM check] Comparing with: \"{cand_title}\"")
                            if semantic_check(incoming_event, cand_event):
                                print(f"  [LLM match] Found duplicate via semantic check")
                                existing_score = cand_score
                                existing_created = cand_created
                                canonical_id, match_type, flag = _resolve_canonical(
                                    cursor, cand_id, existing_score, existing_created,
                                    float(event_score), "semantic"
                                )
                                break

                    if canonical_id and match_type:
                        if flag == "incoming_is_canonical":
                            cursor.execute('''
                                INSERT INTO events (title, speaker, institution, date, url,
                                    score, raw_content, fingerprint, discovery_source_id, location)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                event_title,
                                event.get("speaker"),
                                event.get("institution"),
                                event_date,
                                event_url,
                                event_score,
                                event.get("reasoning"),
                                compute_fingerprint(event_title, event_date, event_url),
                                source_id,
                                event.get("location")
                            ))
                            new_id = cursor.lastrowid
                            cursor.execute(
                                "UPDATE events SET canonical_event_id = ? WHERE id = ?",
                                (new_id, canonical_id)
                            )
                            print(f"  Duplicate: \"{event_title}\" (id={new_id}) ← existing (id={canonical_id}) via {match_type} (incoming is canonical)")
                        else:
                            cursor.execute('''
                                INSERT INTO events (title, speaker, institution, date, url,
                                    score, raw_content, fingerprint, canonical_event_id, discovery_source_id, location)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                event_title,
                                event.get("speaker"),
                                event.get("institution"),
                                event_date,
                                event_url,
                                event_score,
                                event.get("reasoning"),
                                compute_fingerprint(event_title, event_date, event_url),
                                canonical_id,
                                source_id,
                                event.get("location")
                            ))
                            print(f"  Duplicate: \"{event_title}\" (id={cursor.lastrowid}) → canonical (id={canonical_id}) via {match_type}")
                    else:
                        fp = compute_fingerprint(event_title, event_date, event_url)
                        cursor.execute('''
                            INSERT INTO events (title, speaker, institution, date, url,
                                score, raw_content, fingerprint, discovery_source_id, location)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            event_title,
                            event.get("speaker"),
                            event.get("institution"),
                            event_date,
                            event_url,
                            event_score,
                            event.get("reasoning"),
                            fp,
                            source_id,
                            event.get("location")
                        ))
                        print(f"  New event: \"{event_title}\" (id={cursor.lastrowid})")
                except Exception as e:
                    print(f"Error inserting event: {e}")

            # Mark page as processed
            cursor.execute("UPDATE raw_pages SET processed = 1 WHERE id = ?", (page_id,))
            conn.commit()

        return events

    except Exception as e:
        print(f"Error processing page {page_id}: {e}")
        return []


def _delete_events_for_source(source_id):
    """Delete all events linked to a source, safely handling canonical references."""
    with get_connection() as conn:
        cursor = conn.cursor()
        # First nullify any canonical references pointing to events from this source
        cursor.execute("""
            UPDATE events SET canonical_event_id = NULL
            WHERE canonical_event_id IN (
                SELECT id FROM events WHERE discovery_source_id = ?
            )
        """, (source_id,))
        # Then delete the events themselves
        cursor.execute("DELETE FROM events WHERE discovery_source_id = ?", (source_id,))
        deleted = cursor.rowcount
        conn.commit()
        return deleted


def main():
    MAX_PAGES_PER_RUN = 10

    with get_connection() as conn:
        cursor = conn.cursor()
        # Fetch unprocessed pages
        cursor.execute("""
            SELECT rp.id, rp.url, rp.content, rp.source_id
            FROM raw_pages rp
            WHERE rp.processed = 0
        """)
        unprocessed = cursor.fetchall()

    new_batch = list(unprocessed[:MAX_PAGES_PER_RUN])
    remaining_slots = MAX_PAGES_PER_RUN - len(new_batch)

    reprocess_batch = []
    # If we have room, also re-process some already-processed pages
    if remaining_slots > 0:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rp.id, rp.url, rp.content, rp.source_id
                FROM raw_pages rp
                WHERE rp.processed = 1
                  AND rp.content IS NOT NULL
                ORDER BY rp.fetched_at ASC
                LIMIT ?
            """, (remaining_slots,))
            reprocess_batch = cursor.fetchall()

    pages_to_process = new_batch + reprocess_batch

    if not pages_to_process:
        print("No pages to process.")
        return

    print(f"Processing {len(pages_to_process)} pages "
          f"({len(new_batch)} new, {len(reprocess_batch)} re-process).")

    reprocess_ids = {p[0] for p in reprocess_batch}
    for page_id, url, content, source_id in pages_to_process:
        # If this page was already processed, delete old events first
        is_reprocess = page_id in reprocess_ids
        if is_reprocess:
            deleted = _delete_events_for_source(source_id)
            if deleted > 0:
                print(f"Re-processing page {page_id}: deleted {deleted} existing events.")

        events = process_page(page_id, url, content, source_id)

        if events:
            # Backfill: save event URLs as new sources
            backfilled = backfill_sources_from_events(events, source_id)
            if backfilled > 0:
                print(f"  Backfilled {backfilled} new sources from processor.")
            print(f"Extracted {len(events)} events from page {page_id}")
        else:
            print(f"No events found on page {page_id}")


if __name__ == "__main__":
    main()