## 1. Database Migration

- [x] 1.1 Add `crawl_depth` column to `sources` table via `ALTER TABLE sources ADD COLUMN crawl_depth INTEGER DEFAULT 0`
- [x] 1.2 Add `discovery_source_id` column to `events` table via `ALTER TABLE events ADD COLUMN discovery_source_id INTEGER REFERENCES sources(id)`
- [x] 1.3 Update `src/migrate.py` with the new migration steps

## 2. Structured API Discovery Module

- [x] 2.1 Create `src/api_discovery.py` with Eventbrite API v3 integration (query events endpoint with category `102`, AI/ML keyword filtering, geo-filter within 100km of London)
- [x] 2.2 Add online/virtual event fallback — include events with no venue or tagged "online" regardless of location
- [x] 2.3 Implement Eventbrite rate limiting via `API_CALLS_PER_RUN` and inter-API delay

## 3. Advanced Brave Discovery

- [x] 3.1 Update LLM prompt in `src/discovery.py` to generate domain-targeted queries with `site:` prefixes, scoped to London, Oxbridge, and South East region
- [x] 3.2 Modify `search_and_extract_urls()` to follow Brave Search pagination links (up to 3 pages)
- [x] 3.3 Increase `MAX_QUERIES_PER_RUN` from 3 to 5, make it configurable via env var
- [x] 3.4 Add fallback logic: if LLM returns insufficient domain-targeted queries, append queries from `BRAVE_DOMAIN_FILTERS` list
- [x] 3.5 Set `BRAVE_DOMAIN_FILTERS` default to London/Oxbridge/South East domains

## 4. Multi-Level Deep Discovery

- [x] 4.1 Set `crawl_depth` on new sources based on domain match with `HIGHLY_SOURCED_DOMAINS` env var
- [x] 4.2 In `src/fetcher.py`, implement level-2 crawling: for depth=2 sources, fetch sub-pages and extract their links
- [x] 4.3 Add `MAX_DEEP_CRAWL_PER_RUN` configurable limit (default 5) to `src/fetcher.py`
- [x] 4.4 Ensure non-event sub-pages (failing `is_event_link()`) are skipped during deep crawl

## 5. Processor-Stage Backfill

- [x] 5.1 Implement `backfill_sources_from_events()` function that saves event URLs to `sources` table
- [x] 5.2 Integrate backfill into `src/processor.py` main loop — called after each page is processed
- [x] 5.3 Ensure backfilled sources have `last_checked=NULL` so they're fetched in the next pipeline run

## 6. Event Provenance Tracking

- [x] 6.1 Update `src/processor.py` to store `discovery_source_id` on every new event (from the `raw_pages.source_id`)
- [x] 6.2 Update `src/api.py` `/events` endpoint to return `discovery_source_id` field
- [x] 6.3 Add `include_source=true` query parameter to `/events` that joins `sources` table and returns source URL + category

## 7. Discovery Orchestration

- [x] 7.1 Create `src/discovery_stage.py` that imports and runs both `discovery.py` (Brave) and `api_discovery.py` (structured APIs), plus sets `crawl_depth` on new sources
- [x] 7.2 Update `src/pipeline.py` to call `discovery_stage.py` instead of `discovery.py`

## 8. Configuration & Documentation

- [x] 8.1 Add new environment variables to `.env.example`: `EVENTBRITE_API_KEY`, `BRAVE_DOMAIN_FILTERS`, `HIGHLY_SOURCED_DOMAINS`, `MAX_QUERIES_PER_RUN`, `BRAVE_RESULTS_PER_QUERY`, `MAX_DEEP_CRAWL_PER_RUN`, `API_CALLS_PER_RUN`, `API_DELAY_SECONDS`, `LONDON_LAT`, `LONDON_LNG`, `GEO_RADIUS_KM`
- [x] 8.2 Update `README.md` with new API key setup instructions, geo-scope description ("London, surrounding region, and online"), and configuration reference