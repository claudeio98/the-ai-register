# calendar-view Specification

## MODIFIED Requirements

### Requirement: Calendar Visualization
The system SHALL provide a visual representation of events on a calendar grid, showing both event title and score.

#### Scenario: Monthly View
- **WHEN** the user selects "Month View"
- **THEN** the system displays a standard 7-column calendar grid where events are indicated by a score badge followed by a truncated title, or by colored dots with score labels depending on available space.

#### Scenario: Event Selection in Calendar
- **WHEN** the user clicks a date in the calendar
- **THEN** the system filters the main event list to show only events happening on that specific date.

### Requirement: Score Display in Calendar Cells
The system SHALL display each event's relevance score alongside its title within calendar cells.

#### Scenario: Viewing score in calendar cell
- **WHEN** a day cell contains events
- **THEN** each event row in the cell shows a small color-coded score badge (matching the dashboard's scoreClass styling) followed by the event title, truncated to fit.

#### Scenario: Score tooltip in calendar
- **WHEN** the user hovers over a score badge in a calendar cell
- **THEN** the score heuristic tooltip appears (via ℹ️ icon), explaining how scores are calculated.