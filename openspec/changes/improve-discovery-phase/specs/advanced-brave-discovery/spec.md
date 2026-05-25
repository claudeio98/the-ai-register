## ADDED Requirements

### Requirement: System SHALL generate domain-targeted Brave queries

Instead of broad LLM-generated queries, the system SHALL generate queries targeting specific high-yield domains in the **London, surrounding region, and online** scope. The LLM prompt SHALL be scoped to "AI/ML events in London, Oxford, Cambridge, and the surrounding South East region, plus online events." The system SHALL request domain-targeted formats: `site:imperial.ac.uk machine learning events`, `site:ox.ac.uk AI seminar`, etc. The target domains SHALL be configurable via the `BRAVE_DOMAIN_FILTERS` environment variable (default: `imperial.ac.uk,ucl.ac.uk,kcl.ac.uk,ox.ac.uk,cam.ac.uk,lse.ac.uk,qmul.ac.uk,rhul.ac.uk,surrey.ac.uk,reading.ac.uk,deepmind.google,eventbrite.co.uk,eventbrite.com`).

#### Scenario: Domain-targeted query generation for London/Oxbridge
- **WHEN** the system requests search queries from the LLM
- **THEN** the LLM prompt SHALL instruct it to generate queries targeting AI/ML events specifically in London, Oxford, Cambridge, and the South East
- **THEN** at least 3 queries SHALL use `site:` prefixes to specified London-area and Oxbridge domains
- **THEN** the generated queries SHALL be formatted for Brave Search

#### Scenario: Fallback to broad queries
- **WHEN** the LLM returns fewer than 5 queries or all queries lack `site:` prefixes
- **THEN** the system SHALL append fallback domain-targeted queries using the `BRAVE_DOMAIN_FILTERS` list
- **THEN** the system SHALL log "Falling back to pre-built domain-targeted queries"

### Requirement: System SHALL follow pagination on Brave Search results

For each Brave query, the system SHALL fetch up to `BRAVE_RESULTS_PER_QUERY` results (configurable, default: 15, current: 5). If Brave Search returns a `next` page link, the system SHALL follow it up to 3 pages to collect more URLs.

#### Scenario: Multi-page Brave results
- **WHEN** a Brave Search query returns a `next` pagination link
- **THEN** the system SHALL fetch the next page and extract additional URLs
- **THEN** the system SHALL collect URLs until `BRAVE_RESULTS_PER_QUERY` is reached or no more pages exist
- **THEN** the system SHALL save all unique URLs (deduplicated across pages) to the `sources` table

#### Scenario: No pagination link
- **WHEN** a Brave Search query returns results with no `next` link
- **THEN** the system SHALL use only the results from the first page

### Requirement: System SHALL use 5 queries per run instead of 3

The current limit of `MAX_QUERIES_PER_RUN=3` SHALL be increased to 5. The limit SHALL be configurable via the `MAX_QUERIES_PER_RUN` environment variable.

#### Scenario: Increased query limit
- **WHEN** the LLM generates 15 search queries
- **THEN** the system SHALL use the first 5 queries instead of the first 3
- **THEN** the remaining 10 queries SHALL be discarded (regenerated fresh next run)

#### Scenario: Configurable query limit
- **WHEN** `MAX_QUERIES_PER_RUN` is set to 8
- **THEN** the system SHALL use up to 8 queries per run