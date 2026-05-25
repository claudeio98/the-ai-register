"""
Conference Scorer Module

Post-processing phase that aggregates speaker information from related talk/agenda
pages to re-score conference events with a fuller picture of speaker quality.

Flow:
1. After all pages are processed by processor.py, this module runs
2. Groups events by URL directory prefix (e.g., talks under location/london/)
3. For each group, identifies the conference event (broader URL) vs child events
4. Aggregates speaker data from child events
5. Sends aggregated speaker roster to the LLM for re-scoring
6. Updates the conference event's score
"""

import os
import json
import re
import sqlite3
from urllib.parse import urlparse
from db import get_connection
from llm import get_client

CONFERENCE_SCORING_PROMPT = """
You are an AI Events Intelligence agent. You are given a conference/event overview 
page and a list of its individual talk sessions with their speakers.

Based on the FULL speaker roster, assign a score from 0 to 10 using these criteria:

- +4 to +6: Hosted/co-hosted by top-tier AI lab (DeepMind, OpenAI, Meta AI, Google Research, Anthropic, Microsoft Research) OR top-tier university (Imperial, UCL, KCL, Oxford, Cambridge, MIT, Stanford)
- +3 to +5: Organized by recognized conference organizer (AI Accelerator Institute, Gartner, etc.) OR features world-renowned academics/industry leaders
- +2 to +3: Highly relevant to ML/AI, OR features multiple reputable speakers (Hugging Face, Synthesia, Wayve, Luma AI, Stability AI, etc.)
- +1: Moderately relevant AI/ML event with reasonable quality
- -2 to -4: Low-quality, generic non-AI marketing, or irrelevant

Return a JSON object with:
- "score": the numeric score (0-10)
- "reasoning": a short explanation citing the speaker quality and conference merits
"""


def extract_url_prefix(url: str, levels: int = 3) -> str:
    """
    Extract a URL path prefix for grouping events by directory.
    
    Example:
        "https://example.com/a/b/c/d" with levels=3 -> "https://example.com/a/b/c"
        "https://example.com/a/b/c/d" with levels=2 -> "https://example.com/a/b"
    
    Returns the root domain if URL has fewer path components than levels.
    """
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]
        # Take first N path components
        prefix_parts = path_parts[:levels]
        prefix = f"{parsed.scheme}://{parsed.netloc}"
        if prefix_parts:
            prefix += '/' + '/'.join(prefix_parts)
        return prefix
    except Exception:
        return url


def is_conference_event(event) -> bool:
    """
    Determine if an event looks like a conference overview/landing page
    (as opposed to a specific talk).
    
    A conference event typically:
    - Has no specific speaker (speaker is NULL or empty)
    - Has an institution set
    - Has a broader title (not a specific talk title)
    """
    title, speaker, institution = event
    has_speaker = speaker is not None and speaker.strip() != ''
    has_institution = institution is not None and institution.strip() != ''
    
    # If it has both speakers and institution, it's likely a specific talk
    if has_speaker:
        return False
    
    # If it has an institution but no speaker, it's likely a conference landing page
    if has_institution and not has_speaker:
        return True
    
    # No institution, no speaker — ambiguous, skip
    return False


def find_child_events(cursor, conference_id: int, conference_url: str, conference_date: str) -> list:
    """
    Find child events that belong to the same conference.
    
    Strategy: find events that share the same URL prefix (conference URL
    path minus trailing filename like 'register') and have speakers.
    """
    # Determine the directory prefix of the conference URL
    parsed = urlparse(conference_url)
    path = parsed.path.rstrip('/')
    
    # Strip trailing path component if it looks like a page name (register, index, etc.)
    path_parts = [p for p in path.split('/') if p]  # Filter out empty strings
    stripped = False
    if len(path_parts) > 1 and path_parts[-1] in ('register', 'registration', 'index', 'home', 'overview'):
        path_parts = path_parts[:-1]
        stripped = True
    
    if not stripped and len(path_parts) > 1:
        # Also try removing the last component to get the directory level
        prefix_path = '/'.join(path_parts[:-1])
    else:
        prefix_path = '/'.join(path_parts)
    
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    if prefix_path:
        base_url += '/' + prefix_path
    
    print(f"  Looking for child events with URL prefix: {base_url}")
    
    # Find events with URLs starting with this prefix and that have speakers
    cursor.execute("""
        SELECT id, title, speaker, institution, score, url
        FROM events
        WHERE canonical_event_id IS NULL
          AND id != ?
          AND url LIKE ? || '%'
          AND speaker IS NOT NULL
          AND speaker != ''
        ORDER BY score DESC
    """, (conference_id, base_url))
    
    return cursor.fetchall()


def score_conferences():
    """
    Main entry point. Runs after the processor phase.
    
    For each canonical event that looks like a conference page:
    1. Find child talk events (same URL prefix, have speakers)
    2. If children found, aggregate speaker data
    3. Send to LLM for re-scoring
    4. Update the conference event's score
    """
    print("=== Conference Scoring Phase ===")
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Find events that look like conferences (institution but no speaker)
        cursor.execute("""
            SELECT id, title, speaker, institution, score, date, url
            FROM events
            WHERE canonical_event_id IS NULL
              AND (speaker IS NULL OR speaker = '')
              AND (institution IS NOT NULL AND institution != '')
              AND score >= 1
            ORDER BY score
        """)
        
        conference_events = cursor.fetchall()
        print(f"Found {len(conference_events)} potential conference events to check")
        
        updated_count = 0
        
        for event in conference_events:
            event_id, title, _, institution, current_score, date, url = event
            print(f"\nConference: \"{title[:50]}\" (id={event_id}, score={current_score})")
            
            # Find child events
            children = find_child_events(cursor, event_id, url, date)
            
            if not children:
                print(f"  No child events found, skipping")
                continue
            
            print(f"  Found {len(children)} child talk events")
            
            # Build aggregated speaker data
            speaker_lines = []
            for child_id, child_title, speaker, child_inst, child_score, child_url in children:
                speaker_lines.append(
                    f"- \"{child_title}\" by {speaker} ({child_inst or 'unknown'})"
                )
            
            aggregated_speakers = "\n".join(speaker_lines)
            
            # Build the prompt for LLM re-scoring
            prompt = f"""Conference: {title}
Organized by: {institution}
Date: {date}
URL: {url}

Current score: {current_score}/10

Individual talk sessions and speakers:
{aggregated_speakers}

Score this conference based on the FULL speaker roster above."""
            
            print(f"  Sending to LLM for re-scoring with {len(children)} speakers...")
            
            try:
                response = get_client().chat.completions.create(
                    model=os.environ.get("MODEL_NAME", "google/gemma-4-31b-it"),
                    messages=[
                        {"role": "system", "content": CONFERENCE_SCORING_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                data = json.loads(response.choices[0].message.content)
                new_score = data.get("score")
                reasoning = data.get("reasoning", "")
                
                if new_score is not None and isinstance(new_score, (int, float)):
                    new_score = float(new_score)
                    # Only update if new score is higher
                    if new_score > current_score:
                        cursor.execute(
                            "UPDATE events SET score = ? WHERE id = ?",
                            (new_score, event_id)
                        )
                        print(f"  ✓ Score updated: {current_score} → {new_score}")
                        print(f"    Reason: {reasoning[:150]}")
                        updated_count += 1
                    else:
                        print(f"  — No improvement: current={current_score}, new={new_score}")
                else:
                    print(f"  ✗ Invalid LLM response: {data}")
                    
            except Exception as e:
                print(f"  ✗ LLM error: {e}")
        
        conn.commit()
        print(f"\n=== Conference Scoring Complete: {updated_count} events updated ===")


if __name__ == "__main__":
    score_conferences()