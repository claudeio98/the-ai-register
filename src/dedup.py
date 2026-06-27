"""
Dedup module for AI Events Intelligence Pipeline.

Provides title normalization, fingerprint computation, and canonical event
matching to detect and link duplicate event entries.
"""

import re
import hashlib
import os
import json
from urllib.parse import urlparse
from rapidfuzz import fuzz

try:
    from llm import get_client  # when running directly from src/
except ImportError:
    from src.llm import get_client  # when imported via package


def normalize_title(title: str) -> str:
    """
    Normalize an event title for dedup comparison.

    Steps:
    1. Lowercase
    2. Strip punctuation (except hyphens and apostrophes)
    3. Collapse whitespace
    4. Strip leading/trailing whitespace

    Args:
        title: Raw event title.

    Returns:
        Normalized title string.
    """
    if not title:
        return ""
    s = title.lower()
    s = re.sub(r'[^\w\s\'-]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def _canonical_date(date_str: str) -> str:
    """
    Canonicalize a date string to YYYY-MM-DD format where possible.

    Handles ISO dates, partial dates, and date ranges (uses first date).

    Args:
        date_str: Raw date string.

    Returns:
        Canonical date string, or original if unparseable.
    """
    if not date_str:
        return ""
    # Strip time component
    date_str = date_str.split("T")[0].split(" ")[0]
    # Handle ranges like "2026-05-22 to 2026-05-24" -> first date
    if "to" in date_str.lower():
        parts = re.split(r'\s+to\s+', date_str, maxsplit=1, flags=re.IGNORECASE)
        if len(parts) > 1:
            date_str = parts[0].strip()
    # Return as-is if it looks like YYYY-MM-DD or YYYY-MM
    if re.match(r'^\d{4}-\d{2}(-\d{2})?$', date_str):
        return date_str
    return date_str


def extract_domain(url: str) -> str:
    """
    Extract scheme + hostname from a URL for fingerprint composition.

    If the URL has no scheme, prepends https:// so urlparse can
    correctly identify the hostname.

    Args:
        url: Full URL string.

    Returns:
        Domain string like "https://luma.com", or empty string.
    """
    if not url:
        return ""
    try:
        # Ensure a scheme is present so urlparse correctly identifies hostname
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        parsed = urlparse(url)
        scheme = parsed.scheme or "https"
        hostname = parsed.hostname or ""
        return f"{scheme}://{hostname}"
    except Exception:
        return ""


def compute_fingerprint(title: str, date: str, url: str) -> str:
    """
    Compute a deterministic SHA-256 fingerprint for an event.

    Fingerprint = SHA-256(normalized_title | canonical_date | domain)

    Args:
        title: Event title.
        date: Event date.
        url: Event URL.

    Returns:
        Hex digest SHA-256 fingerprint.
    """
    normalized = normalize_title(title)
    canonical_date = _canonical_date(date) if date else ""
    domain = extract_domain(url)
    canonical_string = f"{normalized}|{canonical_date}|{domain}"
    return hashlib.sha256(canonical_string.encode("utf-8")).hexdigest()


def find_canonical(cursor, title: str, date: str, url: str, score: float):
    """
    Find the canonical event for a potential duplicate.

    Date-first matching strategy:
    1. Fingerprint: exact match on (normalized_title|date|domain)
    2. Fuzzy: RapidFuzz token_sort_ratio >= 85 against EXACT same-date events only

    Events on different dates are NOT considered duplicates unless they share
    the exact same title (multi-day conference).

    Args:
        cursor: SQLite cursor.
        title: Event title to check.
        date: Event date.
        url: Event URL.
        score: Event score (used for canonical selection).

    Returns:
        Tuple (canonical_id, match_type) or (None, None) if no match.
        - canonical_id: the ID that should be used as canonical
        - match_type: "fingerprint" or "fuzzy"
    """
    canonical_date = _canonical_date(date) if date else None
    
    # Phase 1: Fingerprint match against canonical events only
    fp = compute_fingerprint(title, date, url)
    cursor.execute(
        "SELECT id, score, created_at FROM events "
        "WHERE fingerprint = ? AND canonical_event_id IS NULL LIMIT 1",
        (fp,)
    )
    row = cursor.fetchone()
    if row:
        return _resolve_canonical(cursor, row[0], row[1], row[2], score, "fingerprint")

    # Phase 2: Fuzzy match against EXACT same-date canonical events only
    # (No ±1 day window - different dates = different events)
    if canonical_date:
        cursor.execute(
            "SELECT id, title, score, created_at FROM events "
            "WHERE date = ? AND canonical_event_id IS NULL",
            (canonical_date,)
        )
    else:
        # If no date, can't do fuzzy match (skip this phase)
        return None, None

    norm_title = normalize_title(title)
    for row in cursor.fetchall():
        existing_id, existing_title, existing_score, existing_created = row
        ratio = fuzz.token_sort_ratio(norm_title, normalize_title(existing_title))
        if ratio >= 85:
            return _resolve_canonical(cursor, existing_id, existing_score,
                                      existing_created, score, "fuzzy")

    return None, None


def _resolve_canonical(cursor, existing_id: int, existing_score: float,
                       existing_created: str, incoming_score: float,
                       match_type: str):
    """
    Determine which event should be canonical when a duplicate is found.

    Strategy: higher score wins; earlier created_at breaks ties.

    If the incoming event should be canonical (higher score), we:
    1. Update the EXISTING event to point to the incoming event
    2. Return a marker so the caller knows the incoming will become canonical

    Args:
        cursor: SQLite cursor.
        existing_id: Existing event ID.
        existing_score: Existing event score.
        existing_created: Existing event created_at timestamp.
        incoming_score: New event's score.
        match_type: "fingerprint" or "fuzzy".

    Returns:
        Tuple (canonical_id, match_type) where canonical_id is the event ID
        that should be the canonical. If incoming_score > existing_score,
        returns (existing_id, match_type) but with a flag that the caller
        should update the existing event later.
    """
    if incoming_score > existing_score:
        # Incoming event becomes canonical.
        # Mark the existing event as a duplicate of the incoming event.
        # (The incoming event hasn't been inserted yet, so we do this
        #  after inserting it with canonical_event_id=NULL)
        return existing_id, match_type, "incoming_is_canonical"
    else:
        # Existing event stays canonical; incoming will link to it.
        return existing_id, match_type, None


def get_duplicate_count(cursor, event_id: int) -> int:
    """
    Count duplicates linked to a canonical event.

    Args:
        cursor: SQLite cursor.
        event_id: Canonical event ID.

    Returns:
        Number of duplicate events pointing to this ID.
    """
    cursor.execute(
        "SELECT COUNT(*) FROM events WHERE canonical_event_id = ?",
        (event_id,)
    )
    return cursor.fetchone()[0]


def semantic_check(event_a, event_b):
    """
    Use LLM to determine if two events are semantically the same.

    Args:
        event_a: Dict with 'title', 'date', 'url' keys.
        event_b: Dict with 'title', 'date', 'url' keys.

    Returns:
        bool: True if events are semantically identical, False otherwise.
    """
    prompt = f"""
    Determine if the following two event descriptions refer to the EXACT same event.
    They are duplicates if they describe the same talk, conference, or workshop, even if the wording differs.
    
    Event A:
    Title: {event_a['title']}
    Date: {event_a['date']}
    URL: {event_a['url']}
    
    Event B:
    Title: {event_b['title']}
    Date: {event_b['date']}
    URL: {event_b['url']}
    
    Return JSON: {{"is_duplicate": true/false, "reason": "short explanation"}}
    """
    try:
        response = get_client().chat.completions.create(
            model=os.environ.get("MODEL_NAME", "deepseek/deepseek-v4-flash"),
            messages=[
                {"role": "system", "content": "You are a precise event deduplication agent. Respond only in JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        return data.get("is_duplicate", False)
    except Exception as e:
        print(f"  Semantic check error: {e}")
        return False