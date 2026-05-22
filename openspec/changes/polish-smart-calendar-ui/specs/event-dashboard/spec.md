## MODIFIED Requirements

### Requirement: Dashboard Overview
The system SHALL provide a summary-driven "Intelligence Hub" that offers high-level insights and curated highlights instead of a simple list of events.

#### Scenario: Viewing the Intelligence Hub
- **WHEN** the user navigates to the Dashboard view
- **THEN** the system displays a set of summary widgets, including:
    - A "Top Highlights" carousel featuring the top 3 highest-scored upcoming events.
    - A "Quick Stats" widget showing the total number of events discovered for the current month.
    - "Smart-Filter" shortcuts (e.g., "This Week", "Next Month") to quickly refine the view.

#### Scenario: Interacting with Highlight Cards
- **WHEN** the user clicks a highlight card in the Dashboard
- **THEN** the system opens the Event Detail Panel for that specific event.
