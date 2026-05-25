## Why

When an event has been discovered from multiple sources (duplicate detections), users currently only see a count badge (`+N more sources`) but cannot access those alternative source URLs. This limits visibility into where the event was also listed, reducing trust and discoverability. Users should be able to explore all available sources for an event directly from the detail panel.

## What Changes

- **API enhancement**: The `/events` endpoint will return a new `other_sources` field on each event, containing an array of `{url, title}` objects from duplicate events linked via `canonical_event_id`. The `include_source` query parameter behavior is already in place but unused — we'll leverage and extend it.
- **Frontend detail panel enhancement**: Below the "Visit Official Site" button in the event detail panel, a dropdown menu will show all other source URLs (from `other_sources`). Each entry is clickable and opens in a new tab.
- **Frontend event list indicator**: The existing `+N more sources` badge remains, providing visual cue that additional sources exist.
- **No breaking changes**: Existing API responses remain backward-compatible; `other_sources` is an added field.

## Capabilities

### New Capabilities
- `other-sources-display`: Display and access alternative source URLs for events in the detail panel, surfaced via a dropdown menu under the primary "Visit Official Site" button.

### Modified Capabilities
- `event-detail-panel`: Update the "list of source URLs" requirement (already in spec) to specify a dropdown UI pattern — primary URL as the main button, additional URLs in an expandable dropdown below it. The spec already requires "a list of source URLs" in the detail panel; this change specifies the concrete UI pattern.
- `event-listing`: No requirement changes — the existing `duplicate_count` badge already signals availability of other sources.

## Impact

- **Backend**: `src/api.py` — add `other_sources` field to the `/events` endpoint by querying duplicate events' URLs for each canonical event.
- **Frontend**: `frontend/index.html` — modify the detail panel's source links section to add a dropdown showing additional source URLs.
- **No new dependencies**: Uses existing data model (events linked via `canonical_event_id`).