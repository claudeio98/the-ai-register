## MODIFIED Requirements

### Requirement: Event Presentation
The system SHALL present events using a modern card-based design that emphasizes visual hierarchy and score importance, with a compact mobile variant.

#### Scenario: Rendering an Event Card on Desktop
- **WHEN** an event is listed in the UI on a viewport of 768px or greater
- **THEN** it SHALL be rendered as a card containing a prominent score badge (color-coded by value), a clear date/time, a concise title, and a brief snippet of the description, matching the existing card layout.

#### Scenario: Rendering a Compact Event Card on Mobile
- **WHEN** an event is listed in the UI on a viewport less than 768px
- **THEN** it SHALL be rendered as a compact card with reduced padding (p-3), inline date text instead of a date badge, score badge, title, institution, and an always-visible hide button.

#### Scenario: Visual Scoring Indicator
- **WHEN** an event has a score $\ge 8$
- **THEN** the score badge SHALL be highlighted in a "high-value" color (e.g., emerald or gold) to immediately attract the user's attention.

