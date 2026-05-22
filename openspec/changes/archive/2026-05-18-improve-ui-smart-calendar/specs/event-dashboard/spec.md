## ADDED Requirements

### Requirement: Dashboard Overview
The system SHALL provide a high-level dashboard that serves as the entry point for event discovery, featuring smart grouping and advanced filtering.

#### Scenario: Viewing the dashboard
- **WHEN** the user navigates to the root dashboard
- **THEN** the system displays a visually structured overview of upcoming AI events, grouped by "Highly Recommended" (high score) and "Upcoming" (chronological).

#### Scenario: Applying a filter
- **WHEN** the user selects a filter (e.g., "London Only" or "Machine Learning")
- **THEN** the system immediately updates the event list to show only matching events with a smooth transition animation.

### Requirement: Visual Timeline/Calendar
The system SHALL provide a temporal visualization of events, allowing users to see the distribution of AI events over time.

#### Scenario: Switching to Timeline View
- **WHEN** the user clicks the "Timeline" toggle
- **THEN** the system renders a vertical timeline where events are placed chronologically, with distinct markers for days and months.

#### Scenario: Date-based Navigation
- **WHEN** the user scrolls through the timeline
- **THEN** the current date marker remains visible, and events are loaded lazily as the user scrolls down.

### Requirement: Responsive Layout Framework
The system SHALL implement a fluid layout that adapts the UI based on the viewport size to ensure a consistent experience on mobile and desktop.

#### Scenario: Mobile View
- **WHEN** the viewport width is less than 768px
- **THEN** the sidebar collapses into a bottom navigation bar, and the event cards stack vertically to maximize readability.

#### Scenario: Desktop View
- **WHEN** the viewport width is 768px or greater
- **THEN** the sidebar is expanded, and the dashboard uses a multi-column grid to display events and a preview panel.

### Requirement: Slide-out Detail Panel
The system SHALL allow users to view deep-dive event details without navigating away from the current list or calendar view.

#### Scenario: Opening event details
- **WHEN** the user clicks an event card in the dashboard or timeline
- **THEN** a panel slides out from the right side of the screen, displaying the full event description, links, and scoring rationale.

#### Scenario: Closing the detail panel
- **WHEN** the user clicks the "Close" button or clicks outside the panel
- **THEN** the panel slides back to the right, returning the user to their exact previous scroll position in the main view.
