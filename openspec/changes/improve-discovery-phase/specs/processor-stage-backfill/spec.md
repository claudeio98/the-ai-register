## ADDED Requirements

### Requirement: System SHALL backfill sources from extracted event URLs

After the processor extracts events from a page using the LLM, the system SHALL collect the `url` field from each extracted event and save any URLs not already in the `sources` table as new sources. This SHALL run after each page is processed.

#### Scenario: New event URL backfilled as source
- **WHEN** the processor extracts an event with a URL that is not in the `sources` table
- **THEN** the system SHALL insert the URL into the `sources` table with `category="discovered"` and `description="Backfilled from processor on source [source_id]"`
- **THEN** the system SHALL log "Backfilled source from event: [url]"

#### Scenario: Event URL already exists in sources
- **WHEN** the processor extracts an event with a URL that already exists in the `sources` table
- **THEN** the system SHALL skip the insert (handled by INSERT OR IGNORE)
- **THEN** the system SHALL log "Source already exists, skipping: [url]"

### Requirement: Backfilled sources SHALL be fetched on the next pipeline run

Backfilled sources SHALL NOT be fetched immediately in the current pipeline run. They SHALL be picked up by the next scheduled pipeline run's fetcher stage. This prevents the current run from growing unboundedly.

#### Scenario: Backfilled source deferred to next run
- **WHEN** a source is backfilled during the processor stage
- **THEN** its `last_checked` SHALL be NULL
- **THEN** the fetcher on the next pipeline run SHALL pick it up as an unvisited source