## Context

The current discovery phase runs at the start of each pipeline execution, before fetching. It has two components:

1. **Dynamic Search Discovery** (`discovery.py`): Asks an LLM for 10-15 search queries, picks the first 3, runs each through Brave Search via a Node.js CLI (`search.js`), and saves up to 5 URLs per query to the `sources` table with `category="discovered"` and `parent_id=NULL`.

2. **Deep Discovery** (`deep_discovery.py`): Runs inside the fetcher. After fetching a page's content, it extracts all links and saves those matching event-related keywords (`/event`, `/seminar`, `/conference`, etc.) while filtering out noise keywords (`login`, `privacy`, `twitter`, etc.). Only one level of crawling is performed.

**Known shortcomings from production data (524 events, 240 sources):**
- Only 50 events (9.5%) come from Brave-discovered sources vs 171 from 60 bootstrap seeds
- Deep discovery has produced just 5 sources → 2 events total
- 301 events (57%) can't be traced back to any source at all
- Brave Search returns noisy, low-yield results for broad queries
- No structured event platform APIs are used (Eventbrite, Luma, Meetup)

**Geographical Scope:**
This design targets **London, the surrounding South East / Oxbridge region, and online events** only. All discovery mechanisms — Brave queries, API calls, and deep crawling — SHALL be scoped accordingly.

**Constraints:**
- Pipeline must complete in a reasonable time (no hanging on slow APIs)
- API keys for external services must be configurable via environment variables
- Must not break the existing database schema — use migrations

## Goals / Non-Goals

**Goals:**
- Increase the number of high-quality sources discovered per pipeline run from ~5-15 to 50+, all scoped to London, surrounding region, and online
- Add Eventbrite API integration with geo-filtering to the target region
- Improve Brave Search queries to be domain-targeted (London/Oxbridge domains) and multi-page
- Extend deep discovery to crawl 2 levels deep on high-value domains in the target region
- Backfill sources from event URLs found by the processor LLM
- Track every event back to its discovery source

**Non-Goals:**
- Changing the processor, notifier, or dedup logic
- Adding real-time or continuous monitoring (still runs on a weekly schedule)
- Replacing Brave Search entirely — it stays as a complementary source
- Building a web UI for discovery configuration (API keys remain in env vars)

## Decisions

### Decision 1: Structured API discovery as a new `discovery_stage` module

**Chosen:** Create `src/discovery_stage.py` that imports `src/discovery.py` (existing Brave Search), `src/api_discovery.py` (new Eventbrite/Luma/Meetup queries), and orchestrates them. Then the existing `pipeline.py` calls `discovery_stage.py` instead of `discovery.py`.

**Alternatives considered:**
- Modify `discovery.py` in-place → Too much code in one file, hard to test each API independently
- Add API calls to `fetcher.py` → Wrong abstraction, discovery and fetching are separate concerns
- Each API as a plugin in a `discovery/` package → Over-engineering for 3 APIs

### Decision 2: Eventbrite as the only structured API (removing Luma and Meetup)

**Chosen:** Use only the Eventbrite API v3. Luma has no official free API (requires reverse-engineering). Meetup API v3 requires a paid plan for commercial use. Eventbrite offers a generous free tier (1,000 calls/hour) with an official, well-documented API v3 that supports geo-filtering, category filtering, and keyword search — covering all the needs for this change.

**API characteristics:**
- **Eventbrite**: Official public API v3. Free tier allows 1,000 calls/hour. Events API returns category (filter to Science & Technology: `102`), subcategory, venue data with lat/lng coordinates, and structured event metadata (title, date, URL, organizer).

### Decision 3: Domain-targeted Brave queries over general queries

**Chosen:** Instead of asking the LLM for generic queries like "AI events London", generate queries targeting specific high-yield domains:
- `site:imperial.ac.uk machine learning seminar`
- `site:ucl.ac.uk AI events`
- `site:ox.ac.uk AI conference`
- `site:cam.ac.uk machine learning talk`
- `site:deepmind.google London events`
- `site:eventbrite.co.uk London AI`

**Why:** Broad Brave queries return mostly aggregator/blog pages (low yield). Domain-specific queries targeting London-area and Oxbridge institutions hit the structured event platforms or exact event calendar subpages directly.

### Decision 4: Two-level deep discovery with per-domain configuration

**Chosen:** When the fetcher visits a source, extract links and classify them as:
- **Level-1 crawl** (current behavior): Save event-keyword-matched links as new sources
- **Level-2 crawl** (new): If the source is from a known high-value domain (e.g., imperial.ac.uk, ucl.ac.uk), also follow links to the sub-pages (e.g., events/2026-may → individual seminar pages)
- This is implemented as a follow-up fetch in the same pipeline run, not recursively

**Configuration:** `HIGHLY_SOURCED_DOMAINS` — a comma-separated env var listing domains where level-2 is enabled. Default: `imperial.ac.uk,ucl.ac.uk,kcl.ac.uk,ox.ac.uk,cam.ac.uk,rhul.ac.uk,surrey.ac.uk,reading.ac.uk,qmul.ac.uk,lse.ac.uk,deepmind.google,eventbrite.co.uk,eventbrite.com`

### Decision 5: Processor-stage backfill via URL extraction

**Chosen:** When the processor's LLM extracts events from a page, it often includes URLs in the event data. After processing, iterate over the extracted events, collect their URLs, and insert any URLs not already in the `sources` table as new sources with `category="discovered"` and a note linking back to the source page.

**Implementation:** A new function `backfill_sources_from_events(processed_events, parent_source_id)` called at the end of `processor.py`'s main loop.

### Decision 6: Provenance tracking via `source_id` on events

**Chosen:** Add a `discovery_source_id INTEGER REFERENCES sources(id)` column to the `events` table. Every event created by the processor stores the `source_id` from the `raw_pages` record that generated it. For backfilled events (processor-stage), store the source page's ID as the provenance.

**Migration:** `ALTER TABLE events ADD COLUMN discovery_source_id INTEGER REFERENCES sources(id)` — existing events set to NULL.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| **Eventbrite free-tier rate limiting** (1,000 calls/hr) | Track call count per run; add configurable per-API rate limit via `API_CALLS_PER_RUN`. Typical run uses <50 calls. |
| **Pipeline takes much longer** with 6x more sources | Keep per-run limits: max 20 new URLs from structured APIs, keep Brave at 5 queries. Users can tune `MAX_SOURCES_PER_RUN`. |
| **Geo-filtering misses relevant events** (e.g., an online event with no location tag) | Always include online/virtual as a fallback category in API queries. |
| **Eventbrite location data may use vague city names** | Use lat/lng + radius filtering rather than text city matching. Default 100km radius includes London to Oxbridge. |
| **Duplicate events from multiple sources** | The existing dedup logic (fingerprint + fuzzy + LLM semantic check) already handles this. |
| **API keys leak or expire** | Fail gracefully with a warning log, skip that API. Pipeline continues with remaining sources. |
| **Database size grows faster** | SQLite handles 10k+ rows easily. Events table already has dedup via canonical_event_id. |

## Geo-Fencing Strategy per Platform

| Platform | Geo-Filtering Method | Default Value |
|---|---|---|
| **Eventbrite** | Use `venue.city` filter or `location.latitude`/`location.longitude` + `location.within` params. | `within: 100km` of London |
| **Brave Search** | Use `site:` queries for London/Oxbridge domains + LLM prompt scoped to "London and surrounding region" | Works by domain targeting, not lat/lng |
| **Processor backfill** | No geo-filtering — backfill ALL event URLs found. Geo-scope is inherent since the source pages are already filtered. | N/A |
| **Deep crawl** | No additional filtering — deep crawl targets already rely on domain matching. | N/A |

Configurable via environment variables:
- `LONDON_LAT=51.5074` / `LONDON_LNG=-0.1278` — centre point
- `GEO_RADIUS_KM=100` — radius from centre. 100km covers London to both Oxford (~85km) and Cambridge (~90km).

## Migration Plan

1. Run `src/migrate.py` to add `discovery_source_id` column to `events` table and `crawl_depth` column to `sources` table
2. Deploy `src/api_discovery.py` (new module) — no breaking changes, existing calls to `discovery.py` still work
3. Update `pipeline.py` to call `discovery_stage.py` instead of `discovery.py`
4. Update `processor.py` to add backfill and store `discovery_source_id`
5. Update `fetcher.py` to support level-2 deep discovery
6. Update `.env.example` with new API keys and geo-configuration
7. Rollback: revert pipeline.py to call discovery.py directly, remove new columns via migration rollback

## Open Questions

- Meetup API v3: What is the exact rate limit for free tier? (Documentation is ambiguous — default to 60 req/min as a safe estimate)
- Should structured API discovery run every pipeline run, or only every N runs? For now, run every time — the APIs paginate and return fresh results each time.
- `GEO_RADIUS_KM`: Default set to 100km to reliably include Cambridge (~90km from London). Users can tighten to 50km for London-only or expand further.
- Meetup and Luma were removed from scope due to paid API access. Could revisit if free tiers become available.