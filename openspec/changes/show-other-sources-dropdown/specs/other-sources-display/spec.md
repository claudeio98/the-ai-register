## ADDED Requirements

### Requirement: Other Sources Dropdown
The system SHALL display alternative source URLs for an event in a collapsible dropdown below the primary "Visit Official Site" button in the detail panel. The dropdown SHALL only appear when the event has at least one alternative source (duplicate_count > 0).

#### Scenario: Displaying other sources dropdown
- **WHEN** the user opens the detail panel for an event that has `duplicate_count > 0`
- **THEN** the system displays a collapsible dropdown below the "Visit Official Site" button with the label "N other source(s)" (where N is the number of alternative sources)

#### Scenario: Expanding the dropdown
- **WHEN** the user clicks on the "N other source(s)" summary
- **THEN** the dropdown expands to show a list of clickable source links, each labeled with the source's title or URL

#### Scenario: Opening an alternative source
- **WHEN** the user clicks an alternative source link in the expanded dropdown
- **THEN** the link opens in a new browser tab

#### Scenario: No alternative sources
- **WHEN** the user opens the detail panel for an event that has `duplicate_count === 0`
- **THEN** the system does not display the "other sources" dropdown below the "Visit Official Site" button

## MODIFIED Requirements

### Requirement: Detail Panel Content
The system SHALL display comprehensive event information in the detail panel, including full description, metadata, external links, and alternative source URLs.

#### Scenario: Rendering event details
- **WHEN** the detail panel is opened for a specific event
- **THEN** the system displays the event title, date, location, full description, the primary event URL as a "Visit Official Site" button, all alternative source URLs in a collapsible dropdown below the primary button, and the AI-generated score rationale.

#### Scenario: External Link Interaction
- **WHEN** the user clicks a source link (primary or alternative) in the detail panel
- **THEN** the link opens in a new browser tab, ensuring the application remains open in the background.