"""
Eventbrite API discovery module.

Queries the Eventbrite API v3 for AI/ML events in London, the surrounding
region (Oxbridge, South East), and online. Respects geo-filtering via
configurable lat/lng/radius and includes online/virtual events as a fallback.
"""

import os
import json
import time
import sqlite3
from datetime import datetime

import requests
from db import get_connection

# --- Configuration from environment ---

EVENTBRITE_API_KEY = os.environ.get("EVENTBRITE_API_KEY", "")

# Geo-centre (default: London)
LONDON_LAT = float(os.environ.get("LONDON_LAT", "51.5074"))
LONDON_LNG = float(os.environ.get("LONDON_LNG", "-0.1278"))
GEO_RADIUS_KM = int(os.environ.get("GEO_RADIUS_KM", "100"))

# Per-run limits
API_CALLS_PER_RUN = int(os.environ.get("API_CALLS_PER_RUN", "60"))
API_DELAY_SECONDS = float(os.environ.get("API_DELAY_SECONDS", "0.5"))


EVENTBRITE_BASE = "https://www.eventbriteapi.com/v3"

# Eventbrite category 102 = "Science & Technology"
CATEGORY_ID = "102"

# Keywords used to filter AI/ML relevance
AI_ML_KEYWORDS = [
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "AI",
    "LLM",
    "large language model",
    "neural network",
    "natural language processing",
    "NLP",
    "computer vision",
    "data science",
    "generative AI",
    "GenAI",
    "MLOps",
    "reinforcement learning",
    "transformer",
    "GPT",
]


def _is_relevant_event(event):
    """
    Check if an event's name or description contains AI/ML keywords.
    Returns True if any keyword matches.
    """
    name = (event.get("name", {}).get("text", "") or "").lower()
    desc = (event.get("description", {}).get("text", "") or "").lower()
    combined = name + " " + desc

    for kw in AI_ML_KEYWORDS:
        if kw.lower() in combined:
            return True
    return False


def _authorized_headers():
    return {
        "Authorization": f"Bearer {EVENTBRITE_API_KEY}",
    }


def _search_events(page=1):
    """
    Search Eventbrite events with geo and category filters.
    Returns parsed JSON response or None on error.
    """
    url = f"{EVENTBRITE_BASE}/events/search"
    params = {
        "categories": CATEGORY_ID,
        "location.latitude": LONDON_LAT,
        "location.longitude": LONDON_LNG,
        "location.within": f"{GEO_RADIUS_KM}km",
        "expand": "venue",
        "page": page,
        "sort_by": "date",
    }

    try:
        resp = requests.get(url, headers=_authorized_headers(), params=params, timeout=15)
        if resp.status_code == 429:
            print(f"  Eventbrite rate limited (429). Sleeping...")
            time.sleep(5)
            return None
        if resp.status_code == 401:
            print("  Eventbrite API: invalid or missing API key (401)")
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"  Eventbrite API error: {e}")
        return None


def _save_events_to_sources(events, query_description):
    """
    Save a list of event page URLs to the sources table.
    Only saves the event URL (the page where details live), not the
    ticket/registration URL, so the fetcher can scrape event content.
    """
    count = 0
    with get_connection() as conn:
        cursor = conn.cursor()
        for event in events:
            # Use the event's explicit URL if available; fall back to the
            # Eventbrite public page URL
            event_url = event.get("url", "")
            if not event_url:
                continue

            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO sources (url, description, category, parent_id, crawl_depth) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (event_url, query_description, "discovered", None, 0),
                )
                if cursor.rowcount > 0:
                    count += 1
            except sqlite3.Error as e:
                print(f"  Error saving source {event_url}: {e}")
        conn.commit()
    return count


def discover_eventbrite_events():
    """
    Main entry point. Queries Eventbrite for AI/ML events in the target
    region, saves discovered URLs to the sources table.

    Returns the number of new sources discovered.
    """
    if not EVENTBRITE_API_KEY:
        print("Eventbrite API key not configured — skipping Eventbrite discovery")
        return 0

    print(f"Discovering Eventbrite events (lat={LONDON_LAT}, lng={LONDON_LNG}, radius={GEO_RADIUS_KM}km)...")

    total_new = 0
    api_calls = 0
    page = 1
    max_pages = 5  # safety limit

    while page <= max_pages and api_calls < API_CALLS_PER_RUN:
        print(f"  Fetching Eventbrite page {page}...")
        data = _search_events(page=page)
        api_calls += 1

        if data is None:
            break

        events = data.get("events", [])
        if not events:
            print("  No more Eventbrite events found.")
            break

        # Filter for AI/ML relevance
        relevant = [e for e in events if _is_relevant_event(e)]
        print(f"  Found {len(events)} raw events, {len(relevant)} AI/ML-relevant.")

        # Save new sources
        desc = f"Eventbrite discovery (page {page})"
        saved = _save_events_to_sources(relevant, desc)
        total_new += saved
        print(f"  Saved {saved} new sources from this page.")

        # --- Online/virtual fallback page ---
        # Check if there are online events on this page (no venue)
        online = [e for e in events if e.get("venue") is None]
        if online:
            online_relevant = [e for e in online if _is_relevant_event(e)]
            if online_relevant:
                online_saved = _save_events_to_sources(online_relevant, "Eventbrite online event discovery")
                total_new += online_saved
                print(f"  Also saved {online_saved} online event sources.")

        # Pagination
        pagination = data.get("pagination", {})
        if not pagination.get("has_more_items", False):
            print("  No more pages.")
            break
        page = pagination.get("page_number", page) + 1

        # Rate limiting: delay between pages
        if api_calls < API_CALLS_PER_RUN:
            time.sleep(API_DELAY_SECONDS)

    print(f"Eventbrite discovery complete. {total_new} new sources found.")
    return total_new


if __name__ == "__main__":
    discover_eventbrite_events()