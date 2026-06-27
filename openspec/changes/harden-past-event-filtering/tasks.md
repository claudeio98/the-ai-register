## 1. Processor — Deploy past-event skip

- [x] 1.1 `_is_future_date` function already written in `processor.py` (lines 142-157)
- [x] 1.2 Past-event skip already written in `process_page()` (lines 192-195)
- [x] 1.3 Skip log message already in place

## 2. Notifier — Deploy + tighten past-event filter

- [x] 2.1 `_is_future_date` function already written in `notifier.py` (lines 207-222)
- [x] 2.2 SQL-level date filter added: `AND (date >= date('now') OR date IS NULL OR date NOT GLOB '____-__-__')`
- [x] 2.3 Python `_is_future_date` post-filter retained for non-ISO formats
- [x] 2.4 Verified via code analysis: YYYY-MM-DD handled by SQL, YYYY-MM/YYYY/null handled by Python fallback

## 3. API — Support past events for Calendar

- [x] 3.1 Added `include_all_dates: bool = False` parameter to `/events` endpoint
- [x] 3.2 When `include_all_dates=true`, the date-based WHERE clause is skipped (returns all events)

## 4. Frontend — Calendar shows past events

- [x] 4.1 Calendar fetches events with `include_all_dates=true` via `fetchCalendarEvents()`
- [x] 4.2 Dashboard continues using `events` ref from default future-only API call
- [ ] 4.3 Test: navigate to a past month in Calendar and verify past events appear (needs production deploy to test with real data)

## 5. Deploy

- [ ] 5.1 Commit all changes with `jj describe`
- [ ] 5.2 Push to production (`jj git push`)
- [ ] 5.3 SSH into server, `git pull && docker compose up -d --build`