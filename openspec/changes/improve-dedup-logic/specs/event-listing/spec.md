# event-listing Specification

## Purpose
Display a clean, scannable list of canonical events for the user to browse and act upon.

## Requirements

### Requirement: Event Presentation
The system SHALL present events using a modern card-based design that emphasizes visual hierarchy and score importance.

#### Scenario: Rendering an Event Card
- **WHEN** an event is listed in the UI
- **THEN** it SHALL be rendered as a card containing a prominent score badge (color-coded by value), a clear date/time, a concise title, and a brief snippet of the description.

#### Scenario: Visual Scoring Indicator
- **WHEN** an event has a score $\ge 8$
- **THEN** the score badge SHALL be highlighted in a "high-value" color (e.g., emerald or gold) to immediately attract the user's attention.

## MODIFIED Requirements

### Requirement: Event Presentation

#### Scenario: Canonical events only in listing
- **WHEN** the UI fetches events for display
- **THEN** it SHALL return only canonical events (rows where `canonical_event_id IS NULL`), excluding soft-linked duplicates

#### Scenario: Duplicate count indicator
- **WHEN** a canonical event has one or more soft-linked duplicates
- **THEN** the UI SHALL display a "duplicate count" badge (e.g., "+2 more sources") on the event card, allowing the user to see how many duplicate entries were merged