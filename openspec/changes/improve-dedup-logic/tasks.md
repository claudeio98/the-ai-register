## 1. Database Migration

- [x] 1.1 Add `canonical_event_id INTEGER REFERENCES events(id)` column to the `events` table via migration script (`src/migrate_dedup.py`)
- [x] 1.2 Create index on `canonical_event_id` for efficient querying of duplicates
- [x] 1.3 Add `fingerprint TEXT UNIQUE` column to the `events` table for hash-based dedup lookups
- [x] 1.4 Create a `migrate_existing_dedup.py` one-time script that backfills `canonical_event_id` for existing duplicates using the same dedup logic

## 2. Dedup Core Module

- [x] 2.1 Create `src/dedup.py` module with title normalization function (lowercase, strip punctuation except hyphens/apostrophes, collapse whitespace)
- [x] 2.2 Implement fingerprint computation: SHA-256 hash of (normalized_title + canonical_date + URL_domain)
- [x] 2.3 Implement `find_canonical()` function that checks fingerprint match first, then falls back to RapidFuzz `token_sort_ratio` (threshold >= 85) against same-date events
- [x] 2.4 Implement `canonical_selection()` function: higher score wins, earlier `created_at` breaks ties
- [x] 2.5 Add RapidFuzz to `requirements.txt`

## 3. Integrate Dedup into Processor

- [x] 3.1 Modify `processor.py` to compute fingerprint and call `find_canonical()` after each event extraction
- [x] 3.2 Update event INSERT logic: if canonical found, set `canonical_event_id` to the canonical event's ID instead of inserting a new row (or set it on insert)
- [x] 3.3 Add dedup logging to stdout: "Duplicate detected: \"Title\" (id=X) → canonical (id=Y) via fingerprint|fuzzy"
- [x] 3.4 Ensure batch processing correct: handle case where multiple events in same batch are duplicates of each other

## 4. Update Event Listing (UI/API)

- [x] 4.1 Modify the FastAPI event listing endpoint to filter out non-canonical events (`WHERE canonical_event_id IS NULL`)
- [x] 4.2 Add a `duplicate_count` field to the API response for each canonical event (number of soft-linked duplicates)
- [x] 4.3 Update the Vue.js frontend to display the duplicate count badge on event cards (e.g., "+2 more sources")

## 5. Testing & Verification

- [x] 5.1 Write unit tests for title normalization (punctuation, casing, whitespace edge cases)
- [x] 5.2 Write unit tests for fingerprint computation (same event different URLs, same title different formatting)
- [x] 5.3 Write unit tests for fuzzy dedup pass (near-duplicate match, genuine non-match)
- [x] 5.4 Write unit tests for canonical selection (higher score wins, tiebreaker by created_at)
- [x] 5.5 Run integration test: process a page with known duplicates and verify only one canonical event per unique talk
- [x] 5.6 Run the migration script on the existing database and verify duplicates are correctly linked