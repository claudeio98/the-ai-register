## MODIFIED Requirements

### Requirement: Calendar Visualization
The system SHALL provide a visual representation of events on a calendar grid, using robust date normalization to ensure markers render correctly regardless of API string formatting.

#### Scenario: Correct Marker Rendering
- **WHEN** an event exists for a specific date (e.g., "2026-05-19")
- **THEN** the system SHALL normalize both the API date and the calendar date to `YYYY-MM-DD` format and render the event marker on the correct day.

#### Scenario: Date-to-Event Navigation
- **WHEN** the user clicks a date in the calendar grid
- **THEN** the system SHALL set the global search query to that date, instantly filtering the Dashboard and Timeline views to show only events for that day.
