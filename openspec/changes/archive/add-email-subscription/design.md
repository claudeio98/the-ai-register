## Context

The AI Events Intelligence Pipeline currently sends high-value event digests to a single hardcoded Gmail address (`GMAIL_USER = "p94126541@gmail.com"` in `src/notifier.py`). There is no subscription system — the notifier is a one-shot script run at the end of the pipeline.

The frontend is a single-page Vue.js app served statically, backed by a FastAPI server at port 8082. The existing notifier uses `gmcli` (a Gmail CLI tool) to send emails.

## Goals / Non-Goals

**Goals:**
- Allow any visitor to subscribe with their email via the frontend
- Store subscriber emails in a new `subscribers` database table
- Send batch digests to all active subscribers when new events are discovered
- Provide a simple unsubscribe mechanism
- Keep the existing digest format and `gmcli` delivery mechanism

**Non-Goals:**
- Email verification (no confirmation link — trust-based subscription)
- Rate limiting or spam protection (acceptable for current scale)
- Custom digest frequency settings per subscriber
- Multi-tenant or role-based access

## Decisions

### 1. Subscriber Table Design
**Decision**: Add a `subscribers` table with `id`, `email` (UNIQUE), `subscribed_at`, and `active` (boolean).
**Rationale**: Simple schema. Soft-delete via `active` column allows re-activation if the same email re-subscribes.
**Alternatives considered**: Using a separate tokens table for unsubscribe. Simpler to use the email itself for unsubscribe.

### 2. API Design for Subscription
**Decision**: Two endpoints:
- `POST /subscribe` — accepts `{ "email": "..." }`, validates format, inserts or reactivates.
- `POST /unsubscribe` — accepts `{ "email": "..." }`, sets `active = false`.
**Rationale**: RESTful, minimal, matches the existing API pattern in `api.py`.

### 3. Notifier Rewrite
**Decision**: Rewrite `notifier.py` to:
1. Query `events` table for new high-scoring events (`status = 'discovered'`, `score >= 7`)
2. If events exist, build one digest (same format as now)
3. Fetch all active subscribers from the `subscribers` table
4. Send the same digest to each subscriber via `gmcli` in a loop
5. Mark events as `notified` and log to `notifications` table
**Rationale**: Single digest per run means all subscribers get the same batch — simple and consistent.
**Alternatives considered**: Individual digests per subscriber (over-engineered for current needs).

### 4. Frontend UX
**Decision**: Add a "Subscribe to Updates" button in the sidebar. Clicking opens a small modal with an email input and "Subscribe" button. Success/error messages appear inline.
**Rationale**: Minimal UI change. No page reload needed — uses the existing Vue.js reactivity.
**Position**: Below the "Dashboard" and "Calendar" nav items in the sidebar.

## Risks / Trade-offs

- **[Risk] Email delivery failures**: `gmcli` may fail for some addresses. **Mitigation**: Notifier logs errors but continues sending to remaining subscribers. Failed sends are caught by `subprocess.CalledProcessError` handler.
- **[Risk] No email validation**: Without confirmation links, invalid emails silently fail. **Mitigation**: Basic format validation on the backend (regex check). Acceptable trade-off for a personal/internal tool.
- **[Trade-off] Single digest per run**: All subscribers get the same content regardless of when they subscribed. This is fine for current scale but may need per-subscriber filtering later.