# event-listing Specification

## MODIFIED Requirements

### Requirement: Event Presentation
The system SHALL present events using a modern card-based design that emphasizes visual hierarchy and score importance, arranged in a single-column list for clarity.

#### Scenario: Rendering an Event Card
- **WHEN** an event is listed in the UI
- **THEN** it SHALL be rendered as a full-width card containing a prominent score badge (color-coded by value), a clear date block, a concise title, institution/source, and a ℹ️ tooltip icon next to the score badge that explains the scoring heuristic on hover.

#### Scenario: Visual Scoring Indicator
- **WHEN** an event has a score $\ge 8$
- **THEN** the score badge SHALL be highlighted in a "high-value" color (e.g., emerald or gold) to immediately attract the user's attention.

### Requirement: Single-Column Layout
The system SHALL display events in a single vertical column for optimal readability.

#### Scenario: Desktop event list layout
- **WHEN** the user views events on a desktop screen (viewport width >= 768px)
- **THEN** events are displayed in a single-column list with full-width cards, rather than a multi-column grid.

#### Scenario: Event list on mobile
- **WHEN** the user views events on a mobile screen (viewport width < 768px)
- **THEN** events continue to display as a single-column stack (existing behavior preserved).

### Requirement: Score Annotation on Event Cards
Each event card SHALL include an interactive score annotation element that explains the scoring system on hover.

#### Scenario: Viewing score explanation
- **WHEN** the user hovers over the ℹ️ icon next to the score badge on an event card
- **THEN** a tooltip popover appears with text: "Scores (0–10) are AI-generated based on relevance, timeliness, and event prominence."