## ADDED Requirements

### Requirement: Events SHALL store their originating source ID

The `events` table SHALL gain a `discovery_source_id INTEGER` column that references `sources(id)`. When the processor creates an event from a raw page, it SHALL store the `source_id` of the raw page that generated it. When the processor backfills a source during the backfill stage (see `processor-stage-backfill` spec), those events SHALL also store the source ID of the page that produced them.

#### Scenario: Event created from raw page stores source_id
- **WHEN** the processor extracts an event from a raw_pages record
- **THEN** the new event's `discovery_source_id` SHALL be set to the raw page's `source_id`
- **THEN** the `discovery_source_id` SHALL be stored in the database

#### Scenario: Existing events have NULL discovery_source_id
- **WHEN** querying events created before this change
- **THEN** those events SHALL have `discovery_source_id = NULL`
- **THEN** the system SHALL handle NULL discovery_source_id gracefully in all queries

### Requirement: API SHALL surface discovery source metadata

The `/events` API endpoint SHALL return the `discovery_source_id` field for each event. A new optional query parameter `include_source=true` SHALL also return the source URL and category alongside `discovery_source_id`.

#### Scenario: API returns discovery_source_id
- **WHEN** a client calls `GET /events`
- **THEN** each event object SHALL include a `discovery_source_id` field (integer or null)

#### Scenario: API returns full source details
- **WHEN** a client calls `GET /events?include_source=true`
- **THEN** each event object SHALL include a `source` object with `id`, `url`, and `category` fields from the `sources` table

#### Scenario: No source found for event
- **WHEN** an event has `discovery_source_id = NULL` or the referenced source has been deleted
- **THEN** the `source` field SHALL be `null` in the response