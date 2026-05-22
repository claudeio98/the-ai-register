import subprocess
import sqlite3
import json
from db import get_connection
from deep_discovery import save_discovered_sources

BROWSER_FETCHER_PATH = "src/browser_fetcher.js"

def fetch_content(url):
    """
    Fetches rendered content using the browser-based fetcher.
    Returns a tuple (content, links) or (None, None).
    """
    print(f"Fetching rendered content from: {url}")
    try:
        # Strict timeout of 45 seconds for browser rendering
        result = subprocess.run(
            ["node", BROWSER_FETCHER_PATH, url],
            capture_output=True,
            text=True,
            check=True,
            timeout=45 
        )
        
        # Parse JSON output from browser_fetcher.js
        data = json.loads(result.stdout)
        return data.get('content'), data.get('links', [])
        
    except subprocess.TimeoutExpired:
        print(f"Timeout fetching {url}")
        return None, None
    except subprocess.CalledProcessError as e:
        print(f"Error fetching {url}: {e}")
        return None, None
    except json.JSONDecodeError:
        print(f"Failed to parse JSON output for {url}")
        return None, None
    except Exception as e:
        print(f"Unexpected error fetching {url}: {e}")
        return None, None

def main():
    with get_connection() as conn:
        cursor = conn.cursor()
        # Filter out sources that have failed too many times
        cursor.execute('''
            SELECT s.id, s.url 
            FROM sources s 
            LEFT JOIN raw_pages rp ON s.id = rp.source_id 
            WHERE (rp.id IS NULL OR rp.fetched_at < datetime('now', '-7 days'))
            AND s.failures < 3
        ''')
        sources = cursor.fetchall()

    if not sources:
        print("No viable sources to fetch.")
        return

    # Keep batch size small to avoid harness timeouts (Task 4.4)
    MAX_FETCHES_PER_RUN = 5 
    sources_to_process = sources[:MAX_FETCHES_PER_RUN]
    
    print(f"Found {len(sources)} viable sources. Fetching a batch of {len(sources_to_process)}.")

    for source_id, url in sources_to_process:
        content, links = fetch_content(url)
        
        # 1. Handle Deep Discovery (Task 4.2)
        if links:
            discovered_count = save_discovered_sources(source_id, links)
            if discovered_count > 0:
                print(f"Deep Discovery: Found and added {discovered_count} new sources from {url}")

        # 2. Update failure count and last_checked
        with get_connection() as conn:
            cursor = conn.cursor()
            if content:
                cursor.execute("UPDATE sources SET last_checked = CURRENT_TIMESTAMP, failures = 0 WHERE id = ?", (source_id,))
            else:
                cursor.execute("UPDATE sources SET last_checked = CURRENT_TIMESTAMP, failures = failures + 1 WHERE id = ?", (source_id,))
            conn.commit()

        # 3. Store raw page content
        if content:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS raw_pages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_id INTEGER,
                        url TEXT,
                        content TEXT,
                        processed INTEGER DEFAULT 0,
                        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (source_id) REFERENCES sources (id)
                    )
                ''')
                cursor.execute("DELETE FROM raw_pages WHERE source_id = ?", (source_id,))
                cursor.execute(
                    "INSERT INTO raw_pages (source_id, url, content) VALUES (?, ?, ?)",
                    (source_id, url, content)
                )
                conn.commit()

if __name__ == "__main__":
    main()
