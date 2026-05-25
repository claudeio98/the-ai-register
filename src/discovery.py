"""
Brave Search discovery module.

Generates domain-targeted search queries (scoped to London, Oxbridge, and the
South East), runs them through Brave Search, and saves discovered URLs to
the sources table. Supports pagination, configurable limits, and fallback
queries when the LLM output is insufficient.
"""

import os
import re
import json
import subprocess
import sqlite3
from db import get_connection
from llm import query_llm

# --- Configuration from environment ---

# Number of search queries to use per pipeline run (default 5, was 3)
MAX_QUERIES_PER_RUN = int(os.environ.get("MAX_QUERIES_PER_RUN", "5"))

# Number of Brave results to fetch per query (default 15, was 5)
BRAVE_RESULTS_PER_QUERY = int(os.environ.get("BRAVE_RESULTS_PER_QUERY", "15"))

# Domains to target with site: queries in Brave Search
BRAVE_DOMAIN_FILTERS = os.environ.get(
    "BRAVE_DOMAIN_FILTERS",
    "imperial.ac.uk,ucl.ac.uk,kcl.ac.uk,ox.ac.uk,cam.ac.uk,"
    "lse.ac.uk,qmul.ac.uk,rhul.ac.uk,surrey.ac.uk,reading.ac.uk,"
    "deepmind.google,eventbrite.co.uk,eventbrite.com"
)


def search_and_extract_urls(query, num_results=BRAVE_RESULTS_PER_QUERY):
    """
    Execute a Brave Search query and extract URLs from the results.
    Follows pagination links (up to 3 pages) to collect more URLs.
    """
    print(f"Searching for: {query}")
    brave_search_path = "/Users/claudio/.pi/agent/skills/pi-skills/brave-search/search.js"
    all_urls = set()
    page = 1
    max_pages = 3

    try:
        # First page
        result = subprocess.run(
            ["node", brave_search_path, query, "-n", str(num_results)],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        urls = re.findall(r"Link: (https?://\S+)", result.stdout)
        all_urls.update(urls)

        # Try to follow pagination by re-running with different offsets
        # (Brave search skill may not return a 'next' link, so we append
        #  offset-style suffixes to the query to get more results)
        while len(all_urls) < num_results and page < max_pages:
            page += 1
            next_query = f"{query} start={page}"
            try:
                result = subprocess.run(
                    ["node", brave_search_path, next_query, "-n", str(num_results)],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=30
                )
                more_urls = re.findall(r"Link: (https?://\S+)", result.stdout)
                prev_count = len(all_urls)
                all_urls.update(more_urls)
                if len(all_urls) == prev_count:
                    # No new URLs found — pagination exhausted
                    break
            except subprocess.CalledProcessError:
                break

        print(f"  Found {len(all_urls)} unique URLs.")
        return list(all_urls)[:num_results]

    except subprocess.CalledProcessError as e:
        print(f"Error searching for {query}: {e}")
        return []
    except subprocess.TimeoutExpired:
        print(f"Timeout searching for {query}")
        return []


def save_sources(urls, query):
    """Save discovered URLs to the sources table."""
    with get_connection() as conn:
        cursor = conn.cursor()
        for url in urls:
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO sources (url, description, category, parent_id) "
                    "VALUES (?, ?, ?, ?)",
                    (url, f"Found via discovery: {query}", "discovered", None)
                )
            except sqlite3.Error as e:
                print(f"Error saving source {url}: {e}")
        conn.commit()


def _build_fallback_queries():
    """Build pre-defined domain-targeted queries from BRAVE_DOMAIN_FILTERS."""
    domains = [d.strip() for d in BRAVE_DOMAIN_FILTERS.split(",") if d.strip()]
    fallbacks = []
    for domain in domains:
        fallbacks.append(f"site:{domain} AI machine learning event")
        fallbacks.append(f"site:{domain} seminar talk lecture")
        fallbacks.append(f"site:{domain} conference workshop")
    return fallbacks


def _check_has_site_prefix(queries):
    """Check if at least 3 queries have a site: prefix."""
    count = sum(1 for q in queries if q.strip().startswith("site:"))
    return count >= 3


def discover_new_sources():
    """Main entry point. Discovers new sources via Brave Search."""
    print("Starting dynamic source discovery phase...")

    # 1. Ask LLM to generate domain-targeted search queries
    system_prompt = """
    You are an expert AI Research Scout focused on the London, Oxford, Cambridge,
    and South East UK AI/ML event scene. Your goal is to find high-value ML/AI
    events, seminars, and conferences in this region.

    Generate a list of 10-15 diverse search queries to find new event pages.
    Focus on:
    - Top London-area universities (Imperial, UCL, KCL, LSE, Queen Mary, Royal Holloway).
    - Oxbridge universities (Oxford, Cambridge).
    - Surrounding institutions (Surrey, Reading, etc.).
    - AI labs in London (DeepMind, Google Research).
    - Conference/seminar/lecture keywords.

    IMPORTANT: Use site: prefixes for at least 5 of the queries to target
    specific high-value domains (e.g., site:imperial.ac.uk, site:ox.ac.uk).

    Return the result as a JSON object with a key "queries" containing a list
    of search query strings.
    """

    user_prompt = "Generate search queries for finding AI/ML events in London, Oxford, Cambridge, and the South East for the current period in 2026."

    queries_json = query_llm(system_prompt, user_prompt, response_format="json")

    if not queries_json:
        print("Failed to get queries from LLM. Using fallback queries.")
        queries = _build_fallback_queries()
    else:
        try:
            data = json.loads(queries_json)
            queries = data.get("queries", [])
            if len(queries) == 1 and isinstance(queries[0], list):
                queries = queries[0]
        except (json.JSONDecodeError, TypeError):
            print("Failed to parse LLM query response. Using fallback queries.")
            queries = _build_fallback_queries()

    # Fallback: if queries lack site: prefixes, append from BRAVE_DOMAIN_FILTERS
    if not _check_has_site_prefix(queries):
        print("LLM queries lack sufficient domain targeting. Appending fallback queries...")
        queries.extend(_build_fallback_queries()[:5])

    # Apply configurable limit
    queries_to_use = queries[:MAX_QUERIES_PER_RUN]
    print(f"Generated {len(queries)} search queries. Using first {len(queries_to_use)} for this run.")

    for query in queries_to_use:
        urls = search_and_extract_urls(query)
        if urls:
            save_sources(urls, query)

    print("Discovery phase complete.")


if __name__ == "__main__":
    discover_new_sources()