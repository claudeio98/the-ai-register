## Context

The AI Events Tracker is a single-page Vue 3 app backed by a FastAPI + SQLite backend. The only user identity mechanism is the `subscribers` table (email + active flag) used for email notifications. There is no session/auth system. The frontend fetches all events via `GET /events` and renders them in dashboard, calendar, highlights, and detail views with no per-user filtering.

The proposal adds the ability for subscribed users to hide events they've already seen or aren't interested in, with their hidden state tied to their subscriber email for cross-device sync.

## Goals / Non-Goals

**Goals:**
- Allow subscribed users to hide any event from all views (dashboard, calendar, highlights, detail panel)
- Persist hidden state server-side, keyed by subscriber email
- Sync hidden state across devices automatically (same email = same hidden set)
- Allow users to unhide events and see a "Hidden Events" management view
- Prompt unsubscribed users to subscribe if they try to hide
- Zero new external dependencies — use existing SQLite + FastAPI infrastructure

**Non-Goals:**
- Full user authentication system (login/password, OAuth, JWT)
- localStorage fallback for unsubscribed users (possible future enhancement)
- Bulk hide/unhide operations
- Analytics on what users hide
- Server-side pagination of hidden events list

## Decisions

### 1. Identity: Reuse Subscriber Email Instead of Device ID

**Decision:** The subscriber's email, sent as a request header, identifies the user for hide/unhide operations.

**Alternatives considered:**
- **Device UUID in localStorage (Option 3)**: Simpler to implement but no cross-device sync. Also fragile if user clears browser data.
- **Full auth system (Option 5/6)**: Far more complex — password hashing, session management, OAuth flows. Overkill for a single-user dashboard feature.
- **No identity (pure localStorage)**: 5-minute implementation but no persistence beyond a single browser.

**Rationale:** The subscriber infrastructure already exists. Users who want cross-device persistence are already subscribed (or can subscribe in one click). This gives server-side persistence with zero auth overhead.

### 2. API Design: Dedicated Endpoints vs. Query Parameter

**Decision:** Use `POST /events/{id}/hide` and `POST /events/{id}/unhide` endpoints, plus a `subscriber_email` query parameter on `GET /events` to filter hidden events.

**Alternatives considered:**
- **PATCH /events/{id} with `hidden: true` payload**: More RESTful, but muddies the events resource with user-specific state. Hidden state is per-user, not per-event.
- **Query parameter `hide_ids=1,2,3` on GET**: Bloats the URL and requires managing a list client-side.

**Rationale:** Dedicated endpoints are self-documenting, easy to call from the frontend, and keep user state separate from event data. The subscriber_email query param on GET is lightweight and optional (unsubscribed users get all events).

### 3. Table Structure: Minimal Join Table

**Decision:** A single `hidden_events` table with columns `(id, event_id, subscriber_email, hidden_at)`.

**Alternatives considered:**
- **JSON column on subscribers table**: Harder to query, index, and manage.
- **Separate per-user hidden_events table per subscriber**: Over-engineered.

**Rationale:** Simple join table, unique constraint on `(event_id, subscriber_email)` prevents duplicates, straightforward to query for filtering.

### 4. Frontend State: Reactive Subscription Email

**Decision:** Add a "Restore Saved View" inline field in the sidebar where users enter their email. Store the email in localStorage and auto-validate on page load.

**User flows:**

**Flow A — Returning subscriber (email in localStorage):**
1. Page loads → localStorage has saved email
2. App auto-validates email against backend (`GET /events?validate_email=...`)
3. If valid → fetch hidden IDs, filter events. Sidebar shows "✅ Restored (email)" with Clear link
4. Hide/Unhide buttons work immediately — zero friction

**Flow B — Subscribed user on a new device (no localStorage):**
1. Page loads → sidebar shows a "Restore Saved View" inline section with email input and a "[Restore]" button
2. User enters their subscription email and clicks Restore → validated against backend
3. If valid → stored in localStorage → hidden IDs fetched → events filtered, sidebar shows "✅ Restored (email)" with Clear link
4. Alternatively: user clicks Hide on any event → prompted to enter email → same result

**Flow C — Not subscribed:**
1. Page loads → sidebar shows the "Restore Saved View" field
2. User clicks Hide on an event → prompted: "Subscribe to save your hidden events across devices"
3. User subscribes → email stored → hidden state ready

**Alternatives considered:**
- **Reactive-only (no Restore field)**: User has to click Hide first to be prompted. Suboptimal for returning subscribers — 5 steps when there should be 0.
- **Always prompt for email on load**: Friction-heavy, annoying for users who don't care about hiding.
- **No persistence**: Lost on tab close.

**Rationale:** The inline "Restore Saved View" field in the sidebar gives returning subscribers a clear, proactive way to "login" without passwords — it explains exactly what it does (restores their hidden events state). localStorage auto-persistence handles the happy path (same browser). The reactive prompt handles discovery for new users. Combined, this covers all three flows with minimal friction.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| **Unsubscribed user enters arbitrary email to bypass prompt** | The backend validates the email exists and is active in the `subscribers` table. Random emails are rejected. This is not a security boundary — it's identity, not auth. |
| **Subscriber email changes or user unsubscribes** | Hidden events become orphaned. Acceptable — the user can re-subscribe to regain access. A cleanup job could remove orphaned hidden_events rows. |
| **Large hidden_events table over time** | The dataset is small (hundreds of events, not millions). A composite index on `(subscriber_email, event_id)` keeps queries fast. |
| **Frontend sends email in plaintext** | This runs locally (localhost:8082). In production, HTTPS would be needed. Acceptable for current deployment model. |
| **User hides an event, then it gets updated with new info** | The hide is per event ID. If the event is re-processed with new data, the hide remains. The user would need to unhide and re-hide. Acceptable — event updates are infrequent. |

## Migration Plan

1. **Database migration** (`src/db.py`): Add `CREATE TABLE IF NOT EXISTS hidden_events` during `init_db()`. No data migration needed — new table.
2. **Backend** (`src/api.py`): Add hide/unhide endpoints, modify `GET /events` to accept optional `subscriber_email` query param and filter.
3. **Frontend** (`frontend/index.html`): Add Connect field in sidebar, state management for subscriber email, hide/unhide buttons on all event surfaces, hidden events management UI.
4. **Verification**: Subscribe with a test email, hide an event, refresh, verify it stays hidden. Unhide, verify it reappears.

**Rollback**: Remove the `hidden_events` table or simply stop sending the subscriber_email header — the GET endpoint defaults to showing all events.

## Open Questions

1. Should the "Hidden Events" management view be in the sidebar, a modal, or a full page view? → **Decision**: A modal (reusing the slide-out panel pattern), accessible from a "Manage Hidden" link in the sidebar.
2. Should calendar cells also get a hide button? → **Decision**: Yes, but as a secondary action (long-press or context menu). For simplicity in v1, focus on event list, highlights, and detail panel. Calendar hide can be done via the detail panel after clicking a calendar event.
3. Batch hide for duplicate events? → **Decision**: Not in scope. Hide individual events only.