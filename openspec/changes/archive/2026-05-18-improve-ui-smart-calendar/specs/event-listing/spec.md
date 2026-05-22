## ADDED Requirements

### Requirement: Event Presentation
The system SHALL present events using a modern card-based design that emphasizes visual hierarchy and score importance.

#### Scenario: Rendering an Event Card
- **WHEN** an event is listed in the UI
- **THEN** it SHALL be rendered as a card containing a prominent score badge (color-coded by value), a clear date/time, a concise title, and a brief snippet of the description.

#### Scenario: Visual Scoring Indicator
- **WHEN** an event has a score $\ge 8$
- **THEN** the score badge SHALL be highlighted in a "high-value" color (e.g., emerald or gold) to immediately attract the user's attention.
