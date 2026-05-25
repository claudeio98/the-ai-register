## 1. Backend: Add `other_sources` to events API

- [x] 1.1 Modify `src/api.py` — in the `get_events` endpoint, after computing `duplicate_count`, add a batch query that fetches `url` and `title` for all duplicate events (`SELECT url, title FROM events WHERE canonical_event_id = ?`) for events that have `duplicate_count > 0`
- [x] 1.2 Use a single grouped batch query to avoid N+1: collect all canonical IDs with `duplicate_count > 0`, query once with `WHERE canonical_event_id IN (...)`, group results by `canonical_event_id`, and assign `other_sources` to each event
- [x] 1.3 Default to empty array `[]` for events with `duplicate_count === 0`

## 2. Frontend: Display other sources dropdown in detail panel

- [x] 2.1 Modify the detail panel template in `frontend/index.html` — add a `<details>` / `<summary>` block below the "Visit Official Site" button, visible only when `detail.other_sources.length > 0`
- [x] 2.2 The `<summary>` text should display "N other source(s)" (e.g., "2 other sources")
- [x] 2.3 Inside the `<details>`, render each source as an `<a href="..." target="_blank">` link, labeled with the source title (falling back to the URL if no title)
- [x] 2.4 Style the dropdown to match the existing UI — small text, rounded corners, subtle borders

## 3. Verify integration

- [x] 3.1 Verify that clicking an event with duplicates in the dashboard shows the "N other source(s)" dropdown in the detail panel
- [x] 3.2 Verify that clicking an event without duplicates does not show the dropdown
- [x] 3.3 Verify that each alternative source link opens in a new tab