import subprocess
import re
import sqlite3
from db import get_connection
from llm import query_llm

def search_and_extract_urls(query):
    print(f"Searching for: {query}")
    # Using the same search logic as before
    try:
        # We need to make sure the BRAVE_SEARCH_PATH is defined
        brave_search_path = "/Users/claudio/.pi/agent/skills/pi-skills/brave-search/search.js"
        result = subprocess.run(
            ["node", brave_search_path, query, "-n", "5"],
            capture_output=True,
            text=True,
            check=True
        )
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
                # Use INSERT OR IGNORE to handle duplicates
                # Seed sources have parent_id = NULL
                cursor.execute(
                    "INSERT OR IGNORE INTO sources (url, description, category, parent_id) VALUES (?, ?, ?, ?)",
                    (url, f"Found via discovery: {query}", "discovered", None)
                )
            except sqlite3.Error as e:
                print(f"Error saving source {url}: {e}")
        conn.commit()

def discover_new_sources():
    print("Starting dynamic source discovery phase...")
    
    # 1. Ask LLM to generate a set of diverse search queries
    system_prompt = """
    You are an expert AI Research Scout. Your goal is to find high-value ML/AI events, seminars, and conferences in London and internationally.
    Generate a list of 10-15 diverse search queries to find new event pages. 
    
    Focus on:
    - Top universities (Imperial, UCL, Oxford, Cambridge, KCL).
    - AI labs (DeepMind, OpenAI, Meta AI, Google Research).
    - Major conferences (NeurIPS, ICML, ICLR, CVPR).
    - Niche AI hubs in London and Europe.
    - Keywords like 'seminar series', 'workshop', 'guest lecture', 'calendar'.
    
    Return the result as a JSON object with a key "queries" containing a list of strings.
    """
    
    user_prompt = "Generate search queries for the current period in 2026."
    
    queries_json = query_llm(system_prompt, user_prompt, response_format="json")
    
    if not queries_json:
        print("Failed to get queries from LLM. Using fallback queries.")
        queries = [
            "Imperial College London AI ML seminar events",
            "UCL AI ML seminar events",
            "Google DeepMind London events seminars",
            "AI conferences Europe 2026"
        ]
    else:
        import json
        data = json.loads(queries_json)
        queries = data.get("queries", [])
        if len(queries) == 1 and isinstance(queries[0], list):
            queries = queries[0]

    # LIMIT for testing: Only use a few queries per run to avoid "stuck" behavior
    MAX_QUERIES_PER_RUN = 3
    queries_to_use = queries[:MAX_QUERIES_PER_RUN]
    print(f"Generated {len(queries)} search queries. Using first {len(queries_to_use)} for this run.")
    
    for query in queries_to_use:
        urls = search_and_extract_urls(query)
        if urls:
            save_sources(urls, query)
    
    print("Discovery phase complete.")

if __name__ == "__main__":
    discover_new_sources()
