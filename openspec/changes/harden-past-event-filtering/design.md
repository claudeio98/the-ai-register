## Context

The production pipeline at `the-ai-register.com` runs every 3 days (cron: `0 6 */3 * *`) and emails a digest of high-value events (score >= 7) to subscribers. Currently, both `processor.py` and `notifier.py` query and insert events with **no date filtering** — all events are processed and all high-scoring events are notified regardless of whether they've already happened.

A `_is_future_date` function and its call sites exist in the uncommitted working tree but were never deployed. The shipped code (commits `5925093` / `701886d`) has zero past-event awareness. On the latest run (June 25), Devworld Conference (dated 2026-05-07, score 8.0) was included in the email.

The Calendar UI also only shows future events because the `/events` API defaults to `show_past=False` and the frontend never requests past data.

## Goals / Non-Goals

**Goals:**
- Processor must skip inserting events whose date is already past (`_is_future_date` check)
- Notifier must exclude past events from digest emails (SQL-level filter, not Python-level)
- Calendar UI must display past events alongside future ones
- All changes deployable with a single `git push + docker compose up -d --build`

**Non-Goals:**
- Deleting existing past events from the database (they should remain for Calendar display)
- Adding a "recency buffer" (skip events within N days of now) — keeping scope minimal
- Changing the notification scheduling or digest frequency
- Rewriting the existing `_is_future_date` logic — it's already correct, just needs deploying

## Decisions

### 1. Deploy existing uncommitted code as-is (processor.py + notifier.py)

The `_is_future_date` function and its call sites in both `processor.py` and `notifier.py` are already written and functionally correct. They just need committing and pushing to production.

**Why not rewrite?** The existing code handles all date formats in the DB (YYYY, YYYY-MM, YYYY-MM-DD) and correctly includes events with null dates (can't rule them out). Rewriting would duplicate effort and risk introducing bugs.

### 2. Move notifier's date filter from Python to SQL

Current uncommitted code filters in Python: `high_value_events = [e for e in all_high_value if _is_future_date(e[4], today)]`. Change this to add `AND date >= date('now')` to the SQL query directly.

**Why SQL?** Two reasons: (a) the notifier fetches ALL high-value events into memory then discards past ones — wasteful as the DB grows; (b) SQL guarantees the filter applies even if Python code path changes later. The SQL `date()` function handles YYYY-MM-DD strings correctly via lexicographic comparison.

**Trade-off**: `date('now')` only matches `YYYY-MM-DD` format events. YYYY and YYYY-MM dates need the Python fallback anyway. Solution: keep a lightweight Python post-filter for non-standard date formats, but move the common case to SQL.

### 3. Calendar UI fetches past events via a separate API path

The Calendar view needs past events. Two approaches considered:

**A) Add `show_past=true` to the main `/events` call** — simplest but forces ALL views to potentially fetch past data. The Dashboard shouldn't need it.

**B) Separate calendar endpoint or parameter** — `/events?calendar=true` that returns all events (past + future). The frontend's Calendar view uses this, Dashboard sticks to the default.

**Chosen: B** via a new parameter `include_all_dates=true`. Keeps the default behavior unchanged (Dashboard stays future-only) and gives the Calendar an explicit opt-in.

### 4. No database migration needed

The `events` table already stores dates as `TEXT` in ISO format (`YYYY-MM-DD`, `YYYY-MM`, or `YYYY`). The `_is_future_date` function handles all three. No schema changes needed.

## Risks / Trade-offs

- **[Low] Year-only dates** (e.g., "2026"): `_is_future_date` considers `2026 >= 2026` as future. A conference dated only "2026" could be in December or already passed. This is acceptable — year-only dates are inherently imprecise and the LLM extraction pipeline is the right place to improve date resolution, not the notification filter.
- **[Low] Pipeline processes events before notification**: The processor inserts events with status `discovered`, then the notifier queries that status. If an event is past, the processor already skips it (Decision 1). No race condition.
- **[Low] Calendar fetches more data**: Adding past events to the Calendar means more rows returned. The production DB has ~200 canonical events (146 past), well within SQLite capacity. No pagination needed yet.
- **[None] Rollback**: The changes are additive (filters + query params). Reverting means removing the filter from notifier SQL and reverting API/frontend changes — all single-line changes per file.