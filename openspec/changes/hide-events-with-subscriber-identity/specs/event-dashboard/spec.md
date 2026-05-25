# event-dashboard Specification (Delta)

## MODIFIED Requirements

### Requirement: Dashboard Overview
The system SHALL provide a high-level dashboard that serves as the entry point for event discovery, featuring smart grouping and advanced filtering. The dashboard SHALL respect the user's hidden events by excluding hidden events from all views (highlights, event list, summary widgets, Next Up) unless the user explicitly toggles "Show Hidden".

#### Scenario: Viewing the dashboard with hidden events
- **WHEN** the user navigates to the root dashboard
- **THEN** the system displays a visually structured overview of upcoming AI events, grouped by "Highly Recommended" (high score) and "Upcoming" (chronological)
- **THEN** events hidden by the user SHALL NOT appear in any dashboard section (highlights, event list, summary widgets, Next Up)

#### Scenario: Show Hidden toggle
- **WHEN** the user clicks a "Show Hidden" toggle
- **THEN** the dashboard SHALL display all events including hidden ones, with a visual indicator (e.g., muted styling) on hidden event cards

### Requirement: Slide-out Detail Panel
The system SHALL allow users to view deep-dive event details without navigating away from the current list or calendar view. The detail panel SHALL include a Hide/Unhide button for subscribed users.

#### Scenario: Opening event details with hide option
- **WHEN** the user clicks an event card in the dashboard or timeline
- **THEN** a panel slides out from the right side of the screen, displaying the full event description, links, and scoring rationale
- **THEN** if the user is subscribed, a "Hide Event" button SHALL be visible at the bottom of the panel
- **THEN** if the event is already hidden, "Unhide Event" SHALL be shown instead

#### Scenario: Hiding from the detail panel
- **WHEN** the user clicks "Hide Event" in the detail panel
- **THEN** the panel SHALL close
- **THEN** the event SHALL be removed from the underlying list

## ADDED Requirements

### Requirement: Hide Button on Highlight Cards
The system SHALL display a hide button on each highlight card for subscribed users.

#### Scenario: Hiding a highlight
- **WHEN** a subscribed user hovers over a highlight card
- **THEN** a small "×" or "Hide" button SHALL appear in the top-right corner
- **WHEN** the user clicks the hide button
- **THEN** the highlight card SHALL animate out and disappear from the section

### Requirement: Hidden Events Sidebar Link
The system SHALL provide a "Manage Hidden" link in the sidebar navigation for subscribed users.

#### Scenario: Accessing hidden events
- **WHEN** a subscribed user clicks "Manage Hidden" in the sidebar
- **THEN** a slide-out panel opens listing all hidden events with Unhide buttons