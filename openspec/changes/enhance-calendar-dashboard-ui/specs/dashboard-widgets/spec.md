## ADDED Requirements

### Requirement: Dashboard Summary Widgets
The system SHALL display summary widgets on the Dashboard to provide immediate insights.

#### Scenario: Viewing Dashboard widgets
- **WHEN** the Dashboard view is active
- **THEN** the system SHALL display:
    - A "This Week" widget showing the count of events happening within the next 7 days.
    - A "Highlights" widget showing the top 3 highest-scored upcoming events.
    - A "This Month" widget showing the total event count for the current month.

#### Scenario: Interacting with Highlights
- **WHEN** the user clicks a highlight card in the dashboard
- **THEN** the event detail panel SHALL open for that event.