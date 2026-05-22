import sqlite3
from db import get_connection

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

def is_event_link(url):
    """
    Determines if a URL is likely to be an event-related page based on its path.
    """
    url_lower = url.lower()
    
    # If any noise keyword is present, reject it
    if any(noise in url_lower for noise in NOISE_KEYWORDS):
        return False
    
    # If any event keyword is present, accept it
    if any(event in url_lower for event in EVENT_KEYWORDS):
        return True
        
    return False

def save_discovered_sources(parent_id, links):
    """
    Filters a list of links and saves high-probability event sources to the database.
    """
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
                    # Use INSERT OR IGNORE to handle deduplication based on the UNIQUE(url) constraint
                    cursor.execute(
                        "INSERT OR IGNORE INTO sources (url, description, category, parent_id) VALUES (?, ?, ?, ?)",
                        (link, f"Deep discovery from source {parent_id}", "discovered", parent_id)
                    )
                    if cursor.rowcount > 0:
                        count += 1
                except sqlite3.Error as e:
                    print(f"Error inserting link {link}: {e}")
            conn.commit()
    except Exception as e:
        print(f"Database error during deep discovery: {e}")
        
    return count

if __name__ == "__main__":
    # Simple test
    test_links = [
        "https://example.com/events/2026-may",
        "https://example.com/about-us",
        "https://example.com/seminars/ai-ethics",
        "https://twitter.com/example"
    ]
    filtered = [l for l in test_links if is_event_link(l)]
    print(f"Filtered links: {filtered}")
