import subprocess
import re
import sqlite3
from db import get_connection

SEARCH_QUERIES = [
    "Imperial College London AI ML seminar events",
    "UCL AI ML seminar events",
    "King's College London AI ML seminar events",
    "University of Oxford AI ML seminar events",
    "University of Cambridge AI ML seminar events",
    "Google DeepMind London events seminars",
    "Google Research London AI events",
    "Meta AI London events",
    "NeurIPS 2026 dates location",
    "ICML 2026 dates location",
    "ICLR 2026 dates location",
    "AI conferences Europe 2026",
]

BRAVE_SEARCH_PATH = "/Users/claudio/.pi/agent/skills/pi-skills/brave-search/search.js"

def search_and_extract_urls(query):
    print(f"Searching for: {query}")
    try:
        result = subprocess.run(
            ["node", BRAVE_SEARCH_PATH, query, "-n", "5"],
            capture_output=True,
            text=True,
            check=True
        )
        # Extract URLs using regex
        urls = re.findall(r"Link: (https?://\S+)", result.stdout)
        return urls
    except subprocess.CalledProcessError as e:
        print(f"Error searching for {query}: {e}")
        return []

def save_sources(urls, query):
    with get_connection() as conn:
        cursor = conn.cursor()
        for url in urls:
            try:
                cursor.execute(
                    "INSERT INTO sources (url, description, category) VALUES (?, ?, ?)",
                    (url, f"Found via search: {query}", "bootstrap")
                )
            except sqlite3.IntegrityError:
                # URL already exists
                pass
        conn.commit()

def main():
    for query in SEARCH_QUERIES:
        urls = search_and_extract_urls(query)
        if urls:
            print(f"Found {len(urls)} URLs for {query}")
            save_sources(urls, query)
        else:
            print(f"No URLs found for {query}")

if __name__ == "__main__":
    main()
