# event-listing Specification (Delta)

## MODIFIED Requirements

### Requirement: Event Presentation
The system SHALL present events using a modern card-based design that emphasizes visual hierarchy and score importance. Each event card SHALL include a "Hide" button for subscribed users.

#### Scenario: Rendering an Event Card with Hide Button
- **WHEN** an event is listed in the UI
- **THEN** it SHALL be rendered as a card containing a prominent score badge (color-coded by value), a clear date/time, a concise title, a brief snippet of the description, and a "Hide" button (visible on hover or as a small "×" icon)
- **WHEN** the user clicks Hide
- **THEN** the card SHALL animate out (fade/slide) and be removed from the list

#### Scenario: Visual Scoring Indicator (unchanged)
- **WHEN** an event has a score $\ge 8$
- **THEN** the score badge SHALL be highlighted in a "high-value" color (e.g., emerald or gold) to immediately attract the user's attention

## ADDED Requirements

### Requirement: Hidden Event Visual Indicator
When "Show Hidden" is active, hidden events SHALL be visually distinguishable from visible events.

#### Scenario: Show Hidden toggle active
- **WHEN** the user toggles "Show Hidden" in the list
- **THEN** hidden events SHALL appear with reduced opacity (e.g., opacity-40) and a muted text style
- **THEN** an "Unhide" button SHALL replace the "Hide" button on hidden event cards