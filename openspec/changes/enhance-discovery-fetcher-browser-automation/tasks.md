## 1. Database Schema Updates

- [x] 1.1 Add `parent_id` column to `sources` table via migration script.
- [x] 1.2 Verify `parent_id` is correctly indexed for lineage tracking.

## 2. Browser Automation Integration

- [x] 2.1 Create a new browser-based fetching utility that interfaces with `agent-browser`.
- [x] 2.2 Implement JS rendering and "wait for element" logic in the fetcher.
- [x] 2.3 Implement "Load More" button detection and interaction.
- [x] 2.4 Implement clean content extraction (Markdown/simplified HTML) from rendered pages.

## 3. Deep Discovery Logic

- [x] 3.1 Implement link extraction logic to identify event-related URLs using keywords.
- [x] 3.2 Implement logic to add discovered URLs to the `sources` table with correct `parent_id`.
- [x] 3.3 Implement deduplication to avoid adding the same URL multiple times.

## 4. Pipeline Integration and Refactoring

- [x] 4.1 Rewrite `src/fetcher.py` to use the new browser-based fetching utility.
- [x] 4.2 Integrate Deep Discovery loop into the `fetcher.py` main execution flow.
- [x] 4.3 Update `src/discovery.py` to handle the initial seed discovery without conflict.
- [x] 4.4 Implement strict timeouts and batching to prevent harness timeouts.

## 5. Verification and Testing

- [ ] 5.1 Test browser fetching on a known JS-heavy event calendar (e.g., a university AI seminar page).
- [ ] 5.2 Verify that "deep" links are being discovered and added to the database.
- [ ] 5.3 Run the full pipeline and ensure events are being processed from discovered sub-links.
