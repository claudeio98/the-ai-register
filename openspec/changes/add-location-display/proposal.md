## Why

Events like ICML (Seoul) are in the database but there's no way to tell where an event takes place. Users need to see whether an event is in London, elsewhere, or online at a glance.

## What Changes

- Add `location` field to the LLM extraction prompt so venue/city is extracted from event pages
- Add `location` column to the events database table
- Return `location` in the API response
- Display a location pill/badge on event cards and in the detail panel

## Capabilities

### New Capabilities
- `location-display`: Extract geographic location from event pages and display it on event cards as a pill badge

### Modified Capabilities

<!-- No existing specs are changing -->

## Impact

- `src/processor.py` — LLM prompt and INSERT statements
- `src/api.py` — SELECT query
- `src/db.py` — schema migration
- `frontend/index.html` — pill badge on event cards