## MODIFIED Requirements

### Requirement: Calendar Visualization
The system SHALL provide a visual representation of events on a calendar grid, with responsive cell sizing for mobile.

#### Scenario: Monthly View on Desktop
- **WHEN** the user selects "Month View" on a viewport of 768px or greater
- **THEN** the system displays a standard 7-column calendar grid where events are indicated by colored score badges and truncated titles, with `min-height: 8rem` per cell.

#### Scenario: Monthly View on Mobile
- **WHEN** the user selects "Month View" on a viewport less than 768px
- **THEN** the system displays a 7-column calendar grid with `min-height: 4rem` per cell, showing only score badges per event (no titles), with a "+N more" indicator for cells with excess events.

#### Scenario: Event Selection in Calendar
- **WHEN** the user clicks a date in the calendar
- **THEN** the system filters the main event list to show only events happening on that specific date.

#### Scenario: Tap to Expand Calendar Cell on Mobile
- **WHEN** the user taps a calendar cell on mobile
- **THEN** the system switches to the dashboard view and filters events for that date.

