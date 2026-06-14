# calendar-view Specification

## Purpose
TBD - created by archiving change improve-ui-smart-calendar. Update Purpose after archive.
## Requirements
### Requirement: Calendar Visualization
The system SHALL provide a visual representation of events on a calendar grid.

#### Scenario: Monthly View
- **WHEN** the user selects "Month View"
- **THEN** the system displays a standard 7-column calendar grid where events are indicated by colored dots or short labels based on their score.

#### Scenario: Event Selection in Calendar
- **WHEN** the user clicks a date in the calendar
- **THEN** the system filters the main event list to show only events happening on that specific date.

## ADDED Requirements

### Requirement: Calendar shows past events
The calendar SHALL display events from past months alongside future events, not just upcoming events.

#### Scenario: Past events visible in calendar months
- **WHEN** the user navigates to a past month in the calendar view
- **THEN** the calendar SHALL display events that occurred during that month

#### Scenario: Past events not shown in Dashboard
- **WHEN** the user views the Dashboard (default view)
- **THEN** only future events SHALL be displayed (past events excluded)

#### Scenario: Calendar fetches all dates from API
- **WHEN** the frontend Calendar view loads
- **THEN** it SHALL request events from the API with a parameter that includes past dates (e.g., `include_all_dates=true`)
- **AND** the Dashboard / main event list SHALL continue to request only future events (default behavior)