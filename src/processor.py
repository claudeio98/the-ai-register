import os
import json
import sqlite3
from openai import OpenAI
from db import get_connection

# Configure OpenAI client for OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY", "OPENROUTER_API_KEY_REMOVED"),
    default_headers={
        "HTTP-Referer": "http://localhost:3000", # Required by OpenRouter
        "X-Title": "AI Events Intelligence Pipeline", # Required by OpenRouter
    }
)

SYSTEM_PROMPT = """
You are an AI Events Intelligence agent. Your task is to extract high-value ML/AI talks and conferences from the provided raw text.

For each event found, extract:
- title: The name of the event.
- speaker: The main speaker (if any).
- institution: The organization hosting or the speaker's affiliation.
- date: The date of the event (ISO format if possible).
- url: The specific URL for the event (if available, otherwise use the page URL).
- score: A score from 0 to 10 based on:
    - +5: DeepMind, OpenAI, Meta AI, Imperial, UCL, KCL, Oxford, Cambridge.
    - +3: World-renowned academics or industry leaders.
    - +2: High relevance to ML/AI business or academic breakthroughs.
    - -2: Low-quality, generic marketing, or irrelevant events.
- reasoning: A short explanation for the score.

Return the results as a JSON object with a key "events" containing a list of these objects. If no events are found, return {"events": []}.
"""

def process_page(page_id, url, content):
    print(f"Processing page {page_id}: {url}")
    try:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "google/gemma-4-31b-it"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"URL: {url}\n\nContent:\n{content}"}
            ],
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        # The prompt asks for a list, but response_format json_object requires a root object.
        # Expecting {"events": [...]}
        return data.get("events", [])
    except Exception as e:
        print(f"Error processing page {page_id}: {e}")
        return []

def main():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, url, content FROM raw_pages WHERE processed = 0")
        pages = cursor.fetchall()

    if not pages:
        print("No unprocessed pages to process.")
        return

    # LIMIT for testing and to avoid harness timeouts
    MAX_PAGES_PER_RUN = 10 
    pages_to_process = pages[:MAX_PAGES_PER_RUN]
    
    print(f"Found {len(pages)} unprocessed pages. Processing a batch of {len(pages_to_process)}.")

    for page_id, url, content in pages_to_process:
        events = process_page(page_id, url, content)
        
        if events:
            with get_connection() as conn:
                cursor = conn.cursor()
                for event in events:
                    try:
                        cursor.execute('''
                            INSERT INTO events (title, speaker, institution, date, url, score, raw_content)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            event.get("title"),
                            event.get("speaker"),
                            event.get("institution"),
                            event.get("date"),
                            event.get("url", url),
                            event.get("score"),
                            event.get("reasoning")
                        ))
                    except Exception as e:
                        print(f"Error inserting event: {e}")
                
                # Mark page as processed
                cursor.execute("UPDATE raw_pages SET processed = 1 WHERE id = ?", (page_id,))
                conn.commit()
            print(f"Extracted {len(events)} events from page {page_id}")
        else:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE raw_pages SET processed = 1 WHERE id = ?", (page_id,))
                conn.commit()
            print(f"No events found on page {page_id}")

if __name__ == "__main__":
    main()
