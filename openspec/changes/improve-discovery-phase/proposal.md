## Why

The current discovery phase finds events through Brave Search (LLM-generated queries) and shallow deep-discovery (keyword-filtered links from fetched pages). Real-world data shows this approach misses most events: only 50 of 524 events come from Brave-discovered sources, and deep discovery has produced just 2 events from 5 sources. The pipeline relies heavily on the 60 bootstrap seeds for 171 events, while 301 events have no tracked source at all. As the bootstrap sources are exhausted, the pipeline will return diminishing results unless discovery improves significantly.

## What Changes

1. **Add Eventbrite API integration** to discover events from a structured event platform — Eventbrite has a generous free tier, official API v3, and strong AI/ML event presence in London and across the UK.
2. **Improve Brave Search discovery** by using domain-targeted queries and a multi-page scraper instead of relying on Brave's top-5 results.
3. **Fix deep discovery to crawl 2 levels deep** on high-value domains instead of stopping at one level, with smarter link classification.
4. **Add processor-stage discovery**: when the LLM extracts events from a page, save any related event URLs it finds as new sources for future fetches.
5. **Track event-to-source provenance properly** so every event can be traced back to where it was found.

## Geographical Scope

This change targets discovery in **London, the surrounding region (Oxbridge, the South East), and online events**. All search queries, API filters, and deep-crawl targets SHALL be scoped to this region:

| Zone | Coverage |
|---|---|
| **London** | All universities (Imperial, UCL, KCL, LSE, Queen Mary, etc.), AI labs (DeepMind London), meetup groups |
| **Surrounding / Oxbridge** | Oxford, Cambridge, Reading, Surrey, and other South East institutions within ~100 miles of London |
| **Online** | Any virtual/online AI/ML event with no location barrier — these are globally discoverable but relevant to a London-based user |
| **Excluded** | In-person events outside the South East (e.g., Berlin, San Francisco, Singapore) — unless they have a London mirror venue or the event is online |

## Capabilities

### New Capabilities
- `structured-api-discovery`: Query the Eventbrite API v3 for AI/ML events in London, the surrounding region, and online, with geo-filtering and rate limiting.
- `advanced-brave-discovery`: Use domain-targeted queries (`site:imperial.ac.uk seminars`, `site:ox.ac.uk AI events`, etc.) targeting London-area and Oxbridge domains, plus follow pagination links to get more than 5 results per query.
- `multi-level-deep-discovery`: Crawl 2 levels deep from high-value sources in the London/South East region (conference → schedule → individual talk pages), with configurable depth limits per domain.
- `processor-stage-backfill`: When the processor's LLM extracts events from a page's content, save any additional event URLs found in the text as new sources in the database.
- `event-provenance-tracking`: Link every event to its source URL via a dedicated `events.source_url` foreign key, and surface source metadata in the API.

### Modified Capabilities
- *(No changes to existing UI specs — this is purely backend infrastructure)*

## Impact

- **New dependencies**: `requests` (already present) + Eventbrite API v3 (requires `EVENTBRITE_API_KEY`)
- **Database**: `events` table gains a `discovery_source_id` column; `sources` table gains a `last_visited_at` and `crawl_depth` column
- **Pipeline order**: Discovery stage grows significantly — may need to split into `discovery` → `discovery-backfill` → `fetcher` for clarity
- **Configuration**: `.env` gains `EVENTBRITE_API_KEY`, `BRAVE_DOMAIN_FILTERS`, `HIGHLY_SOURCED_DOMAINS`, `LONDON_LAT`, `LONDON_LNG`, `GEO_RADIUS_KM`
- **Performance**: Discovery stage will be slower but produce more sources per run. Existing run limits (3 queries, 5 fetches) may need tuning upward.