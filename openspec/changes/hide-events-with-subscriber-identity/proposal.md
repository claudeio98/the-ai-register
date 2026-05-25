## Why

Users want to remove noise from their events dashboard by hiding talks they've already seen or aren't interested in. Currently there is no way to dismiss an event — once fetched, every event stays visible forever. This change adds a "Hide" action that lets subscribed users permanently dismiss events, with the hidden state synced across devices via their existing email subscription.

## What Changes

- Add a `hidden_events` database table linking event IDs to subscriber emails
- Add a backend API endpoint to hide/unhide events (`POST /events/{id}/hide`, `POST /events/{id}/unhide`)
- Modify the `/events` GET endpoint to exclude hidden events (requires subscriber email header)
- Add "Hide" / "Unhide" buttons on event cards, highlights, calendar cells, and the detail panel in the frontend
- When a user is subscribed, their email is used as the identity key for hidden events
- Add a "Connect" inline field in the sidebar where subscribed users can enter their email to sync their hidden state (acts as a lightweight "login")
- Store the connected email in localStorage so it persists across sessions — on page load, auto-validate and fetch hidden IDs
- Hide/unhide buttons are visible on all event surfaces, but only functional when a valid subscriber email is connected
- If an unconnected user clicks Hide, prompt them to subscribe (or enter their existing subscription email)
- Show a "Hidden Events" management view (slide-out panel) listing all hidden events with an "Unhide" button per event

## Capabilities

### New Capabilities
- `event-hiding`: Allow users to hide and unhide events, with persistence tied to their subscriber email identity. Includes backend storage, API endpoints, and frontend hide/unhide UI across all event surfaces.

### Modified Capabilities
- `event-dashboard`: The dashboard's event list, highlights, calendar, and detail panel must show hide/unhide controls and respect the user's hidden state.
- `event-listing`: The filtered/computed listing must exclude hidden events unless the user explicitly toggles "Show Hidden".

## Impact

- **Backend**: `src/db.py` — new table; `src/api.py` — new endpoints + modified `/events` to accept a subscriber email and filter hidden events
- **Frontend**: `frontend/index.html` — hide/unhide buttons on each event surface, hidden state management, email prompt for unsubscribed users, hidden events management UI
- **No new dependencies** — uses existing SQLite + FastAPI + subscriber infrastructure