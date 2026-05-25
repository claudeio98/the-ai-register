# score-annotation Specification

## Purpose
Provide users with a clear understanding of how event relevance scores are calculated, ensuring transparency and helping users interpret the scoring system at a glance.

## Requirements

### Requirement: Score Tooltip on Hover
The system SHALL provide an interactive tooltip that explains the score heuristic when the user hovers over an info icon adjacent to score badges.

#### Scenario: Hovering over score tooltip
- **WHEN** the user hovers over the ℹ️ / ⓘ icon next to any score badge
- **THEN** a tooltip popover appears containing an explanation of the scoring system: scores are AI-generated on a scale of 0–10 based on relevance to AI/ML, timeliness, event prominence, and source quality.

#### Scenario: Tooltip on calendar score badges
- **WHEN** the user hovers over a score badge in a calendar cell
- **THEN** the same score heuristic tooltip appears, with text explaining what the score represents.

#### Scenario: Tooltip dismissal
- **WHEN** the user moves the cursor away from the icon
- **THEN** the tooltip disappears after a short delay (300ms).

### Requirement: Score Explanation in Detail Panel
The system SHALL display the scoring rationale for the selected event within the event detail panel.

#### Scenario: Viewing score rationale in detail panel
- **WHEN** the user opens the event detail panel
- **THEN** the score is displayed alongside a "Why this score?" expandable section or line that describes the factors influencing the event's score (e.g., "High relevance to AI, timely, major institution").

### Requirement: Heuristic Transparency in "Next Up" Widget
The system SHALL include the score explanation icon near the score display in the "Next Up" summary widget.

#### Scenario: Score explanation in dashboard widget
- **WHEN** the user views the "Next Up" widget on the dashboard
- **THEN** the score shown includes a ℹ️ icon that displays the same scoring heuristic on hover.