## Context

The AI Events Intelligence Pipeline currently deduplicates only at the **source level** (`UNIQUE(url)` on the `sources` table), but inserts events with a plain `INSERT` — no constraint, no similarity check. The same conference or talk repeatedly appears in the dashboard because:

1. **The same event lives on different URLs** — a Luma page, a Meetup page, a university events page, and a conference website all point to the same talk.
2. **Re-fetches re-extract** — when a source page is re-fetched (e.g., weekly refresh), the LLM re-discovers the same events and inserts fresh rows.
3. **Overlapping sources** — deep discovery from one page finds links that are already in the `sources` table, leading the LLM to process overlapping content.

The result is a dashboard cluttered with near-identical event cards and the risk of duplicate email notifications.

## Goals / Non-Goals

**Goals:**
- Detect when an incoming event is a duplicate of an existing event with high confidence.
- Merge duplicates into a single canonical event record (preserving the earliest or highest-quality entry).
- Prevent future duplicates from being inserted.
- Clean up existing duplicate data in the database via a one-time migration.
- Keep the solution lightweight — no new external services, no GPU-bound embeddings.

**Non-Goals:**
- Fuzzy title matching across different conferences (e.g., "NeurIPS 2026" vs "International Conference on Neural Information Processing Systems"). If titles are genuinely different but refer to the same event, that's out of scope for this change.
- Real-time dedup (events are processed in batches, so dedup runs during batch insertion).
- Multi-language normalization (all content is English).
- User-facing merge UI (auto-merge only).

## Decisions

### Decision 1: Multi-field hash fingerprint instead of ML-based similarity

**Rationale:** Title normalization + canonical date + normalized URL produces a stable fingerprint. A hash-based approach (`sha256` of a canonical string) is deterministic, zero-latency, and requires no model inference. It catches the vast majority of duplicates (same talk on Luma + Meetup + landing page). An ML/embedding approach would introduce model dependencies, latency, and cost for marginal gain — most duplicates have near-identical titles.

**Alternatives considered:**
- *Fuzzy string matching (RapidFuzz / Levenshtein)* — would catch minor title variations but adds a dependency, tunable threshold, and O(n²) comparison cost. The hash approach is simpler and covers the dominant duplicate pattern.
- *Embedding similarity (sentence-transformers)* — overkill for this scale. If false-negative rate proves too high, embeddings can be added later without breaking the hash approach.

### Decision 2: `canonical_event_id` column on the `events` table instead of a separate link table

**Rationale:** A self-referencing nullable `canonical_event_id` column lets each row point to its canonical parent. Queries for the canonical view are a simple `SELECT ... WHERE canonical_event_id IS NULL UNION ALL SELECT ... FROM events WHERE canonical_event_id IN (...)` or a `GROUP BY canonical_event_id`. A separate junction table adds complexity without benefit at this scale.

**Alternatives considered:**
- *Separate `event_duplicates` table* — cleaner normalization but more joins and migration complexity.
- *Hard merge (DELETE duplicates, keep one)* — irreversible. Soft-linking preserves data for audit and allows future improvements.

### Decision 3: Dedup runs as a post-insert phase in `processor.py`

**Rationale:** The simplest integration point. After the LLM extracts events and inserts them, a dedup function scans the batch for matches against existing events. This avoids modifying the LLM prompt or response format.

**Alternatives considered:**
- *Pre-insert check* — query existing events before every INSERT. Slightly more efficient but couples insert logic with dedup logic. Post-insert is cleaner and easier to test.
- *Separate DEDUP stage in pipeline* — over-engineered for this scope. A single function call in the existing processor is sufficient.

### Decision 4: Title normalization — lowercase, strip punctuation, collapse whitespace

**Rationale:** "Attention Is All You Need" and "Attention is all you need!" should match. A simple normalization pipeline (lowercase → strip punctuation → collapse whitespace) catches formatting differences without needing NLP.

### Decision 5: Use RapidFuzz for a secondary fuzzy pass (if hash misses)

**Rationale:** If the hash-based fingerprint misses a duplicate (e.g., "Deep Learning Workshop – London" vs "Deep Learning Workshop (London)"), a secondary fuzzy pass using RapidFuzz's `token_sort_ratio` with a threshold of ≥85 provides a safety net. We add RapidFuzz as a dependency.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| False positives — two different events incorrectly merged | Keep `canonical_event_id` reversible; always keep the original row as the canonical and only redirect duplicates. Log all merges for audit. |
| Hash misses — genuinely duplicated event with different title formatting | The secondary RapidFuzz pass catches most of these. Threshold is conservative (≥85) to avoid false positives. |
| Performance — O(n²) fuzzy comparison against all existing events | Only compare against events with the same date (or ±1 day). The `events` table is small (~hundreds, not millions). |
| Migration — existing duplicates need cleanup | A dedicated one-time migration script (`migrate_dedup.py`) identifies duplicates via the same algorithm and backfills `canonical_event_id`. |