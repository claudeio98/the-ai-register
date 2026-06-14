## Why

The latest pipeline run (June 25) sent an email containing Devworld Conference — a past event (dated 2026-05-07). The `_is_future_date` check in `processor.py` and `notifier.py` exists only in the uncommitted working tree; the production server runs committed code with **zero past-event filtering**. The result: all high-scoring events get processed and notified regardless of date.

## What Changes

- **Deploy the existing `_is_future_date` filtering** that's already written but uncommitted in both `processor.py` and `notifier.py`
- **Move the past-event filter into the SQL query** in `notifier.py` so it filters at the database level (more reliable than Python list filter)
- **Add past events to the Calendar UI** — the API and frontend currently only show future events in all views

## Capabilities

### New Capabilities
- `past-event-filtering`: Deploy the `_is_future_date` checks already present in the working tree, and tighten them. Processor skips past events at insert time. Notifier excludes past events at query time (SQL-level `WHERE date >= ?` instead of Python list filter).

### Modified Capabilities
- `calendar-view`: Currently only shows future events. Change to display past events in the calendar grid so the user can browse historical data.

## Impact

- `src/processor.py`: Deploy the uncommitted `_is_future_date` check (~3 lines) and the `_is_future_date` function
- `src/notifier.py`: Deploy `_is_future_date` function + rewrite `generate_digest` to filter past events in the SQL query
- `src/api.py`: Support fetching all events (past + future) so the Calendar can show historical data
- `frontend/index.html`: Calendar view needs to fetch past events too; Dashboard stays future-only
- `tests/`: Update/add tests for the date filtering behavior