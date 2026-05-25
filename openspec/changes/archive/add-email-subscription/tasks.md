## 1. Database Migration

- [x] 1.1 Create migration script or extend `src/migrate.py` to add `subscribers` table (`id`, `email` UNIQUE, `subscribed_at`, `active` DEFAULT 1)
- [x] 1.2 Run the migration and verify the table exists in the database

## 2. Backend API — Subscribe & Unsubscribe Endpoints

- [x] 2.1 Add `POST /subscribe` endpoint to `src/api.py` — validates email format, inserts or reactivates subscriber, returns success/error JSON
- [x] 2.2 Add `POST /unsubscribe` endpoint to `src/api.py` — sets `active = false` for matching email, returns confirmation/not-found JSON
- [x] 2.3 Test both endpoints manually with `curl` to confirm correct behavior

## 3. Notifier — Batch Email to All Subscribers

- [x] 3.1 Rewrite `src/notifier.py`: query all active subscribers from `subscribers` table, build one digest for new high-scoring events (`score >= 7`, `status = 'discovered'`), send via `gmcli` to each subscriber in a loop
- [x] 3.2 Keep existing digest format (title, speaker, institution, date, URL, score) and event marking logic (update `status = 'notified'`, insert into `notifications` table)
- [x] 3.3 Add error handling — if `gmcli` fails for one subscriber, log the error and continue with remaining subscribers

## 4. Frontend — Subscribe Button & Modal

- [x] 4.1 Add "Subscribe to Updates" button to the sidebar (below the nav items)
- [x] 4.2 Create a modal component with: email input field, "Subscribe" action button, close button, success/error message area
- [x] 4.3 Wire the modal to call `POST /subscribe` on submit, show inline success (close modal) or error (keep open) messages
- [x] 4.4 Add a minimal "Unsubscribe" link or option in the modal for existing subscribers

## 5. Pipeline Integration

- [x] 5.1 Verify that `src/pipeline.py` correctly runs the updated notifier (no changes needed — it already calls `notifier.py`)
- [x] 5.2 End-to-end test: subscribe an email via frontend, run the pipeline, confirm the digest email is received