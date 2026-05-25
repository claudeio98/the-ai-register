## ADDED Requirements

### Requirement: System SHALL classify domains for crawl depth

The system SHALL assign a crawl depth to each source based on its domain. The `sources` table SHALL gain a `crawl_depth` column (INTEGER, default 0). Domains in the `HIGHLY_SOURCED_DOMAINS` env var (default: `imperial.ac.uk,ucl.ac.uk,kcl.ac.uk,ox.ac.uk,cam.ac.uk,rhul.ac.uk,surrey.ac.uk,reading.ac.uk,qmul.ac.uk,lse.ac.uk,deepmind.google,eventbrite.co.uk,eventbrite.com`) SHALL be assigned depth=2 at insertion time. All other domains SHALL be depth=0 (current behavior — no deep crawl). These domains cover the London-area and Oxbridge institutions that are the primary target for this change.

#### Scenario: High-value domain gets depth=2
- **WHEN** a new source is inserted and its domain matches `HIGHLY_SOURCED_DOMAINS`
- **THEN** the source SHALL have `crawl_depth=2` set in the `sources` table

#### Scenario: Unknown domain gets depth=0
- **WHEN** a new source is inserted and its domain does not match `HIGHLY_SOURCED_DOMAINS`
- **THEN** the source SHALL have `crawl_depth=0`

### Requirement: System SHALL perform level-2 deep crawling on depth=2 sources

When the fetcher processes a source with `crawl_depth=2`, after the default level-1 link extraction, the system SHALL visit the discovered sub-pages in the same pipeline run and extract their links too. Limit: up to `MAX_DEEP_CRAWL_PER_RUN=5` sub-pages per pipeline run (configurable).

#### Scenario: Level-2 crawl on high-value source
- **WHEN** the fetcher finishes extracting links from a depth=2 source
- **THEN** the system SHALL pick up to `MAX_DEEP_CRAWL_PER_RUN` of the newly discovered links
- **THEN** the system SHALL fetch each of those sub-pages and extract their links
- **THEN** any event-keyword-matched links from the sub-pages SHALL be saved as new sources with `parent_id` set to the original source

#### Scenario: Level-2 crawl limit reached
- **WHEN** more than `MAX_DEEP_CRAWL_PER_RUN` sub-pages are available for deep crawling
- **THEN** the system SHALL process only `MAX_DEEP_CRAWL_PER_RUN` sub-pages in this run
- **THEN** the system SHALL log "Deep crawl limit hit for source [id], [N] sub-pages remain"

### Requirement: System SHALL skip level-2 crawl on non-event pages

For each level-2 candidate sub-page, the system SHALL apply the existing `is_event_link()` keyword filter before fetching. If a sub-page's URL does not match event keywords, it SHALL be skipped.

#### Scenario: Non-event sub-page skipped
- **WHEN** a sub-page URL contains noise keywords (login, privacy, terms, etc.) or lacks event keywords
- **THEN** the system SHALL skip fetching that sub-page
- **THEN** the system SHALL log "Skipping non-event sub-page: [url]"