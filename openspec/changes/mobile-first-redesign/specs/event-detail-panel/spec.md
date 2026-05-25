## MODIFIED Requirements

### Requirement: Detail Panel Content
The system SHALL display comprehensive event information in the detail panel, using a bottom sheet on mobile and the existing right-slide panel on desktop.

#### Scenario: Rendering event details on desktop
- **WHEN** the detail panel is opened on a viewport of 768px or greater
- **THEN** the system displays the event title, date, location, full description, a list of source URLs, and the AI-generated score rationale, sliding in from the right.

#### Scenario: Rendering event details on mobile (bottom sheet)
- **WHEN** the detail panel is opened on a viewport less than 768px
- **THEN** the system displays a bottom sheet sliding up from the bottom with a drag handle, containing the event title, date, location, full description, score rationale, and action buttons. The backdrop behind the sheet is tappable to dismiss.

#### Scenario: External Link Interaction
- **WHEN** the user clicks a source link in the detail panel
- **THEN** the link opens in a new browser tab, ensuring the application remains open in the background.

