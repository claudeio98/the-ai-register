## 1. Database

- [x] 1.1 Add `hidden_events` table to `src/db.py` init_db: `(id, event_id, subscriber_email, hidden_at)` with UNIQUE(event_id, subscriber_email) constraint and composite index

## 2. Backend API

- [x] 2.1 Add `POST /events/{event_id}/hide` endpoint — validates subscriber email via X-Subscriber-Email header, checks subscriber is active, INSERT OR IGNORE into hidden_events, returns 200 with `{"success": true}` or 403 for inactive email
- [x] 2.2 Add `POST /events/{event_id}/unhide` endpoint — validates subscriber email, DELETE from hidden_events, returns 200
- [x] 2.3 Add `GET /events/hidden` endpoint — accepts `subscriber_email` query param, returns list of hidden event IDs and event data for the Hidden Events management view
- [x] 2.4 Add `GET /events/check-subscriber` endpoint — accepts `email` query param, returns `{"active": true/false, "email": "..."}` to validate a stored subscriber email on page load
- [x] 2.5 Modify `GET /events` — accept optional `subscriber_email` query param, add LEFT JOIN / NOT IN filter to exclude events in hidden_events for that email (if email is provided and subscriber is active)

## 3. Frontend — Sidebar Connect Field

- [x] 3.1 Add a "Restore Saved View" section in the sidebar (below navigation, above Subscribe button) — heading, email input + "[Restore]" button, and hint text: "Enter your subscription email to sync your hidden events across devices."
- [x] 3.2 On Restore click, call `GET /events/check-subscriber?email=...` — if active, store email in localStorage, show "✅ Restored (email)" with "Clear" link; if inactive, show error: "No subscription found for this email."
- [x] 3.3 On Clear click, remove email from localStorage, reset sidebar to show Restore field, clear hiddenIds
- [x] 3.4 On app mount, if a stored email exists in localStorage, auto-validate via `/events/check-subscriber` — if valid, auto-restore; if invalid, clear and show Restore field

## 4. Frontend — State & Filtering

- [x] 4.1 Add `subscriberEmail` Vue ref (from localStorage or Connect field), plus `hiddenIds` reactive Set
- [x] 4.2 When subscriberEmail is set, fetch hidden IDs via `GET /events/hidden?subscriber_email=...` and populate `hiddenIds`
- [x] 4.3 Modify `filtered` computed property to exclude events whose ID is in `hiddenIds`
- [x] 4.4 When subscriberEmail changes (connect/disconnect), refetch events with the new email filter

## 5. Frontend — Hide/Unhide Buttons

- [x] 5.1 Add "Hide" button (× icon, visible on hover) to event list cards — calls `POST /events/{id}/hide` with subscriber_email param, removes card, adds ID to `hiddenIds`
- [x] 5.2 Add "Hide" button to highlight cards (visible on hover, top-right corner) — same behavior as 5.1
- [x] 5.3 Add "Hide Event" button to the detail panel (bottom, near the "Visit Official Site" button) — hides event and closes panel
- [x] 5.4 If user clicks Hide but no subscriber email is stored, show subscribe modal instead

## 6. Frontend — Hidden Events Management

- [x] 6.1 Add "Manage Hidden" link to the sidebar (below the Subscribe button, visible only when connected)
- [x] 6.2 Create a slide-out panel (reusing the existing transition/panel pattern) showing all hidden events — each entry shows title, date, and an "Unhide" button
- [x] 6.3 On Unhide click, call `POST /events/{id}/unhide`, remove from hidden list panel, remove from `hiddenIds`
- [x] 6.4 If no events are hidden, show "No hidden events" in the panel

## 7. Verification

- [x] 7.1 Start the backend and frontend, subscribe with an email, hide an event — verify it disappears and stays hidden on page refresh
- [x] 7.2 Unhide the event from the Hidden Events panel — verify it reappears
- [x] 7.3 Connect via the sidebar Connect field on a fresh browser (no localStorage) — verify hidden state loads correctly
- [x] 7.4 Verify auto-connect works on page reload (stored email in localStorage)
- [x] 7.5 Verify Disconnect clears state and hide buttons show prompt again
- [x] 7.6 Verify unsubscribed users are prompted to subscribe when clicking Hide
- [x] 7.7 Verify all existing backend tests still pass (no regressions)
- [x] 7.8 Verify existing structural checks pass (no regressions in content, tags, or computed properties)