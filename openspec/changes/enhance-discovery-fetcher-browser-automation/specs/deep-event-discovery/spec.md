## ADDED Requirements

### Requirement: Link Discovery and Filtering
The system SHALL analyze rendered pages for links that likely lead to event-related content.

#### Scenario: Identifying Event Links
- **WHEN** a page is fetched
- **THEN** the system SHALL identify links containing keywords like "event", "calendar", "seminar", "workshop", or "schedule" and extract their absolute URLs.

### Requirement: Automated Discovery Queueing
The system SHALL automatically add newly discovered event-related URLs to the discovery queue.

#### Scenario: New URL Discovery
- **WHEN** the system identifies a new event-related URL on a page
- **THEN** the system SHALL insert it into the `sources` table as a new source, marking it as "discovered".

### Requirement: Source Lineage Tracking
The system SHALL track the relationship between the page where a link was found and the link itself.

#### Scenario: Tracking Parent Source
- **WHEN** a new URL is added to the `sources` table via deep discovery
- **THEN** the system SHALL store the ID of the source page as the `parent_id` for the new source.
