"""
Discovery stage orchestrator.

Runs both Brave Search discovery and Eventbrite API discovery,
then sets crawl_depth on newly inserted sources.
"""

import sqlite3
from db import get_connection
from deep_discovery import get_crawl_depth_for_url


def _update_crawl_depth_for_new_sources():
    """
    Update crawl_depth for any sources that have crawl_depth=0 (the default)
    but belong to high-value domains. This ensures that sources inserted by
    discovery modules before crawl_depth was set get the correct depth.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        # Find sources with depth=0 that haven't been checked yet
        cursor.execute("SELECT id, url FROM sources WHERE crawl_depth = 0")
        rows = cursor.fetchall()
        updated = 0
        for source_id, url in rows:
            depth = get_crawl_depth_for_url(url)
            if depth > 0:
                cursor.execute(
                    "UPDATE sources SET crawl_depth = ? WHERE id = ?",
                    (depth, source_id)
                )
                updated += 1
        conn.commit()
        if updated > 0:
            print(f"Updated crawl_depth for {updated} existing sources.")


def main():
    print("=== Discovery Stage ===")

    # 1. Brave Search discovery
    print("\n--- Brave Search Discovery ---")
    try:
        from discovery import discover_new_sources
        discover_new_sources()
    except Exception as e:
        print(f"Brave Search discovery failed: {e}")

    # 2. Eventbrite API discovery
    print("\n--- Eventbrite API Discovery ---")
    try:
        from api_discovery import discover_eventbrite_events
        discover_eventbrite_events()
    except Exception as e:
        print(f"Eventbrite API discovery failed: {e}")

    # 3. Set crawl_depth on any sources that may have been missed
    print("\n--- Setting crawl depths ---")
    _update_crawl_depth_for_new_sources()

    print("\n=== Discovery Stage Complete ===")


if __name__ == "__main__":
    main()