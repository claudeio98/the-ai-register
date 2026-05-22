## ADDED Requirements

### Requirement: Inline Event Previews
The system SHALL display event title and score directly within calendar grid cells, replacing simple dot markers.

#### Scenario: Viewing calendar with event previews
- **WHEN** the calendar grid is displayed for a month
- **THEN** each cell that has events SHALL show a truncated event title and a colored score badge, in addition to the day number.

#### Scenario: Cell without events
- **WHEN** a calendar day has no events
- **THEN** only the day number SHALL be displayed.