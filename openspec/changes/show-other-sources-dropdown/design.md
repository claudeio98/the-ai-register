## Context

The current event detail panel shows a single "Visit Official Site" button linking to the event's `url` field. When an event has been detected from multiple sources (duplicate events linked via `canonical_event_id` in the database), users only see a `+N more sources` badge on the event card — but can't access those alternative URLs from the detail panel.

The existing `event-detail-panel` spec already requires "a list of source URLs" to be shown, but the implementation only provides a single button. The `duplicate_count` field exists on the API response but no actual source URLs are returned.

## Goals / Non-Goals

**Goals:**
- Return other source URLs (from duplicate events) in the API response for each canonical event
- Display a collapsible dropdown menu below the "Visit Official Site" button showing all alternative source URLs
- Each alternative source URL opens in a new tab when clicked
- Maintain backward compatibility — existing API consumers see no breaking changes

**Non-Goals:**
- Adding pagination for large numbers of duplicate sources (unlikely to exceed 5-10)
- Reordering or ranking alternative sources
- Editing or removing alternative sources from the UI
- Showing source metadata beyond URL (e.g., discovery source name, timestamp)

## Decisions

### 1. Backend: Add `other_sources` to the events endpoint directly (not a separate endpoint)

**Decision:** Add a new `other_sources` field to the existing `/events` endpoint response, computed in the same loop that adds `duplicate_count`. This avoids an extra API call per event or a separate endpoint that the frontend would need to manage.

**Alternative considered:** A dedicated `/events/{id}/sources` endpoint. Rejected because it adds N+1 API calls when loading the event list, and the data is simple enough to inline.

**Alternative considered:** Using the existing `include_source` query parameter. Rejected because `include_source` is for discovery provenance, not duplicate URLs — mixing concerns would be confusing.

### 2. Data model: Query `events` table WHERE `canonical_event_id = ?`

**Decision:** For each canonical event, query `SELECT url, title FROM events WHERE canonical_event_id = ? ORDER BY score DESC` to get alternative sources. The `url` and `title` fields from duplicate records provide both the link and a label for the dropdown.

**Rationale:** The existing dedup system already links duplicates via `canonical_event_id`. No schema changes are needed — this is a read-side enhancement only.

### 3. Frontend: Dropdown with toggle arrow, below the primary button

**Decision:** Add a `<details>` / `<summary>` HTML element (native disclosure widget) below the "Visit Official Site" button. It shows "N other source(s)" as the summary text. When opened, it lists each source as a clickable link that opens in a new tab.

**Alternative considered:** A custom JavaScript dropdown with hover/click state. Rejected in favor of native `<details>` which requires zero JS for toggle behavior, is accessible by default, and matches the existing pattern (score rationale uses `<details>/<summary>`).

### 4. Frontend: Fetch `other_sources` via the events API (no new fetches)

**Decision:** The frontend already receives `detail` (the clicked event object) from the events list. The `other_sources` array will be part of that object. No additional API calls needed when opening the detail panel.

## Risks / Trade-offs

- **[Performance]** Querying duplicates per event adds N queries for N canonical events. **Mitigation:** Use a single batch query (`WHERE canonical_event_id IN (...)?`) grouped by canonical_id, then merge into responses. Only enabled when events have `duplicate_count > 0` — many events won't need the extra query.
- **[Edge case]** An event with zero duplicates has `other_sources: []`. **Mitigation:** The dropdown simply doesn't render when the array is empty — no UI impact.
- **[Mobile]** The dropdown adds vertical space below the button on mobile. **Mitigation:** The `<details>` element is compact (summary line only) and only expands on interaction.