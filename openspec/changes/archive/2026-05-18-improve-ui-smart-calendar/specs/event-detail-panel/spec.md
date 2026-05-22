## ADDED Requirements

### Requirement: Detail Panel Content
The system SHALL display comprehensive event information in the detail panel, including full description, metadata, and external links.

#### Scenario: Rendering event details
- **WHEN** the detail panel is opened for a specific event
- **THEN** the system displays the event title, date, location, full description, a list of source URLs, and the AI-generated score rationale.

#### Scenario: External Link Interaction
- **WHEN** the user clicks a source link in the detail panel
- **THEN** the link opens in a new browser tab, ensuring the application remains open in the background.
