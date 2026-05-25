## Why

The current deduplication logic relies solely on `INSERT OR IGNORE` with a `UNIQUE(url)` constraint in the `sources` table. This is insufficient because the same event or talk is often hosted on multiple URLs (e.g., a landing page, a Luma page, and a Meetup page). This results in duplicate event entries in the database, cluttering the dashboard and requiring manual cleanup.

## What Changes

- Implement a more sophisticated deduplication mechanism that goes beyond URL matching.
- Introduce a "similarity scoring" or "identity matching" phase during event processing.
- Modify the event insertion logic to check for existing similar events before creating a new record.
- Create a mechanism to link duplicate events or merge them into a single canonical entry.

## Capabilities

### New Capabilities
- `event-deduplication`: A system to detect and merge duplicate event entries based on titles, dates, and descriptions rather than just URLs.

### Modified Capabilities
- `event-listing`: Update the listing to ensure only the canonical version of a deduplicated event is shown.

## Impact

- `src/processor.py`: Logic for event scoring and insertion will need to include deduplication checks.
- `src/db.py` (or equivalent): Database schema may need updates to track canonical event IDs or links between duplicates.
- `data/events.db`: Existing duplicate data will need to be handled/migrated.
