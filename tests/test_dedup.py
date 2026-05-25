"""
Unit tests for the dedup module.

Tests: title normalization, fingerprint computation, canonical selection,
and rapidfuzz fuzzy matching integration.
"""

import os
import sys
import tempfile
import sqlite3

# Ensure src is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.dedup import (
    normalize_title,
    compute_fingerprint,
    _canonical_date,
    extract_domain,
    get_duplicate_count,
)


# ---------------------------------------------------------------------------
# 5.1 Title normalization tests
# ---------------------------------------------------------------------------

def test_normalize_title_lowercases():
    assert normalize_title("Deep Learning Workshop") == "deep learning workshop"


def test_normalize_title_strips_punctuation():
    result = normalize_title("Attention Is All You Need!")
    assert result == "attention is all you need"
    assert "!" not in result


def test_normalize_title_preserves_hyphens():
    result = normalize_title("State-of-the-Art ML")
    assert result == "state-of-the-art ml"


def test_normalize_title_preserves_apostrophes():
    result = normalize_title("O'Reilly AI Conference")
    assert result == "o'reilly ai conference"


def test_normalize_title_collapses_whitespace():
    result = normalize_title("Deep   Learning   Workshop")
    assert result == "deep learning workshop"


def test_normalize_title_strips_leading_trailing():
    result = normalize_title("  Hello World  ")
    assert result == "hello world"


def test_normalize_title_handles_unicode_dash():
    """En-dash is punctuation (not a hyphen), so it gets stripped."""
    result = normalize_title("Deep Learning – London")
    assert result == "deep learning london"


def test_normalize_title_empty_string():
    assert normalize_title("") == ""


def test_normalize_title_none():
    assert normalize_title(None) == ""


# ---------------------------------------------------------------------------
# 5.2 Fingerprint computation tests
# ---------------------------------------------------------------------------

def test_fingerprint_deterministic():
    fp1 = compute_fingerprint("Test Talk", "2026-06-15", "https://luma.com/event")
    fp2 = compute_fingerprint("Test Talk", "2026-06-15", "https://luma.com/event")
    assert fp1 == fp2


def test_fingerprint_different_urls_differ():
    fp1 = compute_fingerprint("Test Talk", "2026-06-15", "https://luma.com/event")
    fp2 = compute_fingerprint("Test Talk", "2026-06-15", "https://meetup.com/event")
    assert fp1 != fp2


def test_fingerprint_same_domain_same_fingerprint():
    """Same domain, different paths should produce same fingerprint (domain-normalized)."""
    fp1 = compute_fingerprint("Test Talk", "2026-06-15", "https://luma.com/events/123")
    fp2 = compute_fingerprint("Test Talk", "2026-06-15", "https://luma.com/events/456")
    assert fp1 == fp2


def test_fingerprint_title_normalization_matters():
    """Punctuation/casing differences should produce same fingerprint (title is normalized)."""
    fp1 = compute_fingerprint("Attention Is All You Need!", "2026-06-15", "https://example.com")
    fp2 = compute_fingerprint("Attention is all you need", "2026-06-15", "https://example.com")
    assert fp1 == fp2


def test_fingerprint_date_affects_result():
    fp1 = compute_fingerprint("Test Talk", "2026-06-15", "https://example.com")
    fp2 = compute_fingerprint("Test Talk", "2026-06-16", "https://example.com")
    assert fp1 != fp2


def test_fingerprint_no_url():
    fp = compute_fingerprint("Test Talk", "2026-06-15", "")
    assert len(fp) == 64  # SHA-256 hex digest


def test_fingerprint_no_title():
    fp = compute_fingerprint("", "2026-06-15", "https://example.com")
    assert len(fp) == 64


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------

def test_canonical_date_iso():
    assert _canonical_date("2026-05-22") == "2026-05-22"


def test_canonical_date_with_time():
    assert _canonical_date("2026-05-22T14:30:00") == "2026-05-22"


def test_canonical_date_range():
    result = _canonical_date("2026-05-22 to 2026-05-24")
    assert result == "2026-05-22"


def test_canonical_date_empty():
    assert _canonical_date("") == ""


def test_extract_domain_full_url():
    assert extract_domain("https://luma.com/events/123?ref=home") == "https://luma.com"


def test_extract_domain_no_scheme():
    assert extract_domain("luma.com/events") == "https://luma.com"


def test_extract_domain_empty():
    assert extract_domain("") == ""


# ---------------------------------------------------------------------------
# 5.4 Canonical selection tests (via database integration)
# ---------------------------------------------------------------------------

def test_get_duplicate_count():
    """Verify get_duplicate_count returns correct count."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            score REAL,
            canonical_event_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute("INSERT INTO events (title, score) VALUES ('Canonical', 8)")
    cursor.execute("INSERT INTO events (title, score, canonical_event_id) VALUES ('Dup1', 6, 1)")
    cursor.execute("INSERT INTO events (title, score, canonical_event_id) VALUES ('Dup2', 7, 1)")
    
    count = get_duplicate_count(cursor, 1)
    assert count == 2, f"Expected 2 duplicates, got {count}"
    conn.close()


# ---------------------------------------------------------------------------
# Run tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Collect all test functions
    tests = [fn for fn in globals().values() if callable(fn) and fn.__name__.startswith("test_")]
    passed = 0
    failed = 0
    for test_fn in sorted(tests, key=lambda f: f.__name__):
        try:
            test_fn()
            print(f"  ✓ {test_fn.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {test_fn.__name__}: {e}")
            failed += 1
    print(f"\n{passed}/{passed + failed} tests passed")
    if failed:
        exit(1)