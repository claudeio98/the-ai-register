import os
import json
import sqlite3
from db import get_connection
from dedup import compute_fingerprint, find_canonical, _resolve_canonical, get_duplicate_count, semantic_check
from llm import get_client

SYSTEM_PROMPT = """
You are an AI Events Intelligence agent. Your task is to extract high-value ML/AI talks and conferences from the provided raw text.

For each event found, extract:
- title: The name of the event.
- speaker: The main speaker (if any).
- institution: The organization hosting or the speaker's affiliation.
- date: The date of the event (ISO format if possible).
- url: The specific URL for the event (if available, otherwise use the page URL).
- score: A score from 0 to 10 based on the criteria below.
- reasoning: A short explanation for the score.

Scoring criteria (0-10 scale):
- +4 to +6: Event hosted or co-hosted by a top-tier AI lab (DeepMind, OpenAI, Meta AI, Google Research, Anthropic, Microsoft Research) OR a top-tier university (Imperial, UCL, KCL, Oxford, Cambridge, MIT, Stanford). Recognized keynote speakers from these orgs push toward the higher end.
- +3 to +5: Event organized by a recognized conference organizer (e.g., AI Accelerator Institute, Gartner) OR featuring world-renowned academics or industry leaders as speakers.
- +2 to +3: Event highly relevant to ML/AI business or academic breakthroughs, OR featuring multiple reputable speakers from notable companies (e.g., Hugging Face, Synthesia, Wayve, Luma AI, Stability AI).
- +1: Moderately relevant AI/ML event with reasonable quality but no big names.
- -2 to -4: Low-quality, generic non-AI marketing, or events clearly irrelevant to ML/AI.

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


def process_page(page_id, url, content, source_id):
    """
    Process a page: extract events via LLM, insert them with provenance,
    and backfill any new source URLs found.
    Returns the list of extracted events (or empty list).
    """
    print(f"Processing page {page_id}: {url}")
    try:
        response = get_client().chat.completions.create(
            model=os.environ.get("MODEL_NAME", "google/gemma-4-31b-it"),
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
                    event_date = event.get("date", "")
                    event_score = event.get("score", 0) or 0

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
                                    score, raw_content, fingerprint, discovery_source_id)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                event_title,
                                event.get("speaker"),
                                event.get("institution"),
                                event_date,
                                event_url,
                                event_score,
                                event.get("reasoning"),
                                compute_fingerprint(event_title, event_date, event_url),
                                source_id
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
                                    score, raw_content, fingerprint, canonical_event_id, discovery_source_id)
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
                                canonical_id,
                                source_id
                            ))
                            print(f"  Duplicate: \"{event_title}\" (id={cursor.lastrowid}) → canonical (id={canonical_id}) via {match_type}")
                    else:
                        fp = compute_fingerprint(event_title, event_date, event_url)
                        cursor.execute('''
                            INSERT INTO events (title, speaker, institution, date, url,
                                score, raw_content, fingerprint, discovery_source_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            event_title,
                            event.get("speaker"),
                            event.get("institution"),
                            event_date,
                            event_url,
                            event_score,
                            event.get("reasoning"),
                            fp,
                            source_id
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


def main():
    with get_connection() as conn:
        cursor = conn.cursor()
        # Fetch unprocessed pages along with their source_id
        cursor.execute("""
            SELECT rp.id, rp.url, rp.content, rp.source_id
            FROM raw_pages rp
            WHERE rp.processed = 0
        """)
        pages = cursor.fetchall()

    if not pages:
        print("No unprocessed pages to process.")
        return

    MAX_PAGES_PER_RUN = 10
    pages_to_process = pages[:MAX_PAGES_PER_RUN]

    print(f"Found {len(pages)} unprocessed pages. Processing a batch of {len(pages_to_process)}.")

    for page_id, url, content, source_id in pages_to_process:
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