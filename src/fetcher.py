import subprocess
import sqlite3
import json
import os
from urllib.parse import urlparse
from db import get_connection

BROWSER_FETCHER_PATH = os.path.join(os.path.dirname(__file__), "browser_fetcher.js")

# Max level-2 sub-pages to crawl per pipeline run
MAX_DEEP_CRAWL_PER_RUN = int(os.environ.get("MAX_DEEP_CRAWL_PER_RUN", "5"))

# Max sources to fetch per run (existing limit)
MAX_FETCHES_PER_RUN = int(os.environ.get("MAX_FETCHES_PER_RUN", "5"))

# Domains eligible for level-2 deep crawling
HIGHLY_SOURCED_DOMAINS = os.environ.get(
    "HIGHLY_SOURCED_DOMAINS",
    "imperial.ac.uk,ucl.ac.uk,kcl.ac.uk,ox.ac.uk,cam.ac.uk,"
    "rhul.ac.uk,surrey.ac.uk,reading.ac.uk,qmul.ac.uk,lse.ac.uk,"
    "deepmind.google,eventbrite.co.uk,eventbrite.com"
).split(",")

# Keywords used to identify potential event-related pages
EVENT_KEYWORDS = {
    'event', 'calendar', 'seminar', 'workshop', 'schedule',
    'lecture', 'talk', 'conference', 'symposium', 'webinar', 'meetup'
}

# Keywords used to filter out noise/non-content pages
NOISE_KEYWORDS = {
    'login', 'signup', 'privacy', 'terms', 'about', 'contact',
    'cookie', 'search', 'social', 'twitter', 'facebook', 'linkedin', 'instagram'
}


def _extract_domain(url):
    """Extract the domain (e.g., 'imperial.ac.uk') from a URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return ""


def _is_highly_sourced_domain(url):
    """Check if a URL's domain is in the HIGHLY_SOURCED_DOMAINS list."""
    domain = _extract_domain(url)
    for hsd in HIGHLY_SOURCED_DOMAINS:
        hsd = hsd.strip()
        if hsd and hsd in domain:
            return True
    return False


def get_crawl_depth_for_url(url):
    """Determine the crawl depth for a URL based on its domain.
    Returns 2 for high-value domains, 0 otherwise."""
    return 2 if _is_highly_sourced_domain(url) else 0


def is_event_link(url):
    """Determines if a URL is likely to be an event-related page based on its path."""
    url_lower = url.lower()
    if any(noise in url_lower for noise in NOISE_KEYWORDS):
        return False
    if any(event in url_lower for event in EVENT_KEYWORDS):
        return True
    return False


def save_discovered_sources(parent_id, links):
    """Filters a list of links and saves high-probability event sources to the database.
    Sets crawl_depth based on the discovered URL's domain."""
    if not links:
        return 0

    event_links = [link for link in links if is_event_link(link)]
    if not event_links:
        return 0

    count = 0
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            for link in event_links:
                try:
                    depth = get_crawl_depth_for_url(link)
                    cursor.execute(
                        "INSERT OR IGNORE INTO sources (url, description, category, parent_id, crawl_depth) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (link, f"Deep discovery from source {parent_id}", "discovered", parent_id, depth)
                    )
                    if cursor.rowcount > 0:
                        count += 1
                except sqlite3.Error as e:
                    print(f"Error inserting link {link}: {e}")
            conn.commit()
    except Exception as e:
        print(f"Database error during deep discovery: {e}")

    return count


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


def _store_raw_page(source_id, url, content):
    """Store fetched page content in raw_pages table."""
    with get_connection() as conn:
        cursor = conn.cursor()
        _ensure_raw_pages_table(cursor)
        cursor.execute("DELETE FROM raw_pages WHERE source_id = ?", (source_id,))
        cursor.execute(
            "INSERT INTO raw_pages (source_id, url, content) VALUES (?, ?, ?)",
            (source_id, url, content)
        )
        conn.commit()


def _update_source_status(source_id, success):
    """Update failure count and last_checked for a source."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if success:
            cursor.execute(
                "UPDATE sources SET last_checked = CURRENT_TIMESTAMP, failures = 0 WHERE id = ?",
                (source_id,)
            )
        else:
            cursor.execute(
                "UPDATE sources SET last_checked = CURRENT_TIMESTAMP, failures = failures + 1 WHERE id = ?",
                (source_id,)
            )
        conn.commit()


def _fetch_and_store(source_id, url, is_deep_crawl=False):
    """
    Fetch a single URL, store its content, perform deep discovery.
    If is_deep_crawl is True, this is a level-2 fetch and we skip
    further deep discovery to avoid infinite recursion.
    """
    content, links = fetch_content(url)

    # Level-1 deep discovery (only for top-level fetches)
    if links and not is_deep_crawl:
        discovered_count = save_discovered_sources(source_id, links)
        if discovered_count > 0:
            print(f"  Deep Discovery: Found and added {discovered_count} new sources from {url}")
    elif links and is_deep_crawl:
        print(f"  (Level-2 crawl — skipping further deep discovery from {url})")

    # Update source status
    _update_source_status(source_id, success=(content is not None))

    # Store page content
    if content:
        _store_raw_page(source_id, url, content)

    return content, links


def _perform_level_2_crawl(source_id, url, links):
    """
    For sources with crawl_depth=2, perform level-2 crawling:
    fetch sub-pages (up to MAX_DEEP_CRAWL_PER_RUN) and extract their links.
    """
    if not links:
        return

    # Get the source's crawl_depth
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT crawl_depth FROM sources WHERE id = ?", (source_id,))
        row = cursor.fetchone()

    if not row or row[0] < 2:
        return  # Not eligible for level-2 crawl

    # Filter links to event-related ones only
    sub_page_links = [link for link in links if is_event_link(link)]
    if not sub_page_links:
        print(f"  No event-related sub-pages to deep-crawl from source {source_id}.")
        return

    sub_pages_to_crawl = sub_page_links[:MAX_DEEP_CRAWL_PER_RUN]
    print(f"  Level-2 crawl: fetching up to {len(sub_pages_to_crawl)} sub-pages from source {source_id}...")

    for sub_url in sub_pages_to_crawl:
        # Save sub-page as a source if not already present
        sub_depth = get_crawl_depth_for_url(sub_url)
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO sources (url, description, category, parent_id, crawl_depth) "
                "VALUES (?, ?, ?, ?, ?)",
                (sub_url, f"Level-2 deep crawl from source {source_id}", "discovered", source_id, sub_depth)
            )
            conn.commit()

        # Fetch the sub-page (flagged as deep crawl to avoid recursion)
        sub_content, sub_links = fetch_content(sub_url)
        if sub_content:
            _store_raw_page_for_deep_crawl(sub_url, sub_content)
        if sub_links:
            # Save links from sub-page as new sources (level-3, but these won't be crawled)
            save_discovered_sources(source_id, sub_links)


def _ensure_raw_pages_table(cursor):
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


def _store_raw_page_for_deep_crawl(url, content):
    """Store a level-2 sub-page's content as raw_pages."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM sources WHERE url = ?", (url,))
        row = cursor.fetchone()
        if row:
            source_id = row[0]
            _ensure_raw_pages_table(cursor)
            cursor.execute("DELETE FROM raw_pages WHERE source_id = ?", (source_id,))
            cursor.execute(
                "INSERT INTO raw_pages (source_id, url, content) VALUES (?, ?, ?)",
                (source_id, url, content)
            )
            conn.commit()


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

    sources_to_process = sources[:MAX_FETCHES_PER_RUN]
    print(f"Found {len(sources)} viable sources. Fetching a batch of {len(sources_to_process)}.")

    for source_id, url in sources_to_process:
        content, links = _fetch_and_store(source_id, url)

        # Level-2 deep crawl if eligible
        if links:
            _perform_level_2_crawl(source_id, url, links)


if __name__ == "__main__":
    main()