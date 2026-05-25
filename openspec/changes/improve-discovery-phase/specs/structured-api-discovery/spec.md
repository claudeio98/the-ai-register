## ADDED Requirements

### Requirement: System SHALL query Eventbrite API for AI/ML events in London region

The system SHALL query the Eventbrite API v3 (`https://www.eventbriteapi.com/v3/`) to discover AI/ML events. The Eventbrite API key SHALL be configured via the `EVENTBRITE_API_KEY` environment variable. If the key is missing, the system SHALL skip Eventbrite discovery and log a warning.

The system SHALL apply the following filters:
- **Category**: `102` (Science & Technology) subcategory
- **Keywords**: AI/ML relevance keywords (e.g., "machine learning", "artificial intelligence", "deep learning", "AI")
- **Geo**: `location.latitude`/`location.longitude` + `location.within` (default: 100km from London `51.5074, -0.1278`, configurable via `GEO_RADIUS_KM`)
- **Online events**: Events with no venue or tagged as online SHALL be included regardless of location

#### Scenario: Eventbrite API returns London-region events
- **WHEN** the system has a valid `EVENTBRITE_API_KEY` and queries the Eventbrite API with category `102`, AI/ML keywords, and location within 100km of London
- **THEN** the system SHALL parse the response and extract event URLs, titles, dates, and organizer information
- **THEN** the system SHALL save up to 20 new event source URLs to the `sources` table with `category="discovered"`

#### Scenario: Eventbrite API key is missing
- **WHEN** the `EVENTBRITE_API_KEY` environment variable is not set
- **THEN** the system SHALL log a warning: "Eventbrite API key not configured — skipping Eventbrite discovery"
- **THEN** the system SHALL continue execution without error

#### Scenario: Eventbrite API returns no AI/ML events
- **WHEN** the Eventbrite API returns results but none match AI/ML keyword filters within the geo-region
- **THEN** the system SHALL log "No AI/ML events found on Eventbrite for this query"
- **THEN** the system SHALL continue normally

### Requirement: System SHALL apply per-API rate limits and delays

The system MUST respect configurable per-API rate limits to avoid being blocked. Configuration is via environment variables: `API_CALLS_PER_RUN=60` (default, per API) and `API_DELAY_SECONDS=1` (default delay between API calls to the same platform).

#### Scenario: Per-run API call limit exceeded
- **WHEN** a discovery API has made `API_CALLS_PER_RUN` calls already in this pipeline run
- **THEN** the system SHALL stop querying that API for the remainder of the run
- **THEN** the system SHALL log "API call limit reached for [API name], skipping remaining calls"