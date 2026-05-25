# event-dashboard Specification

## MODIFIED Requirements

### Requirement: Dashboard Overview

The system SHALL provide a high-level dashboard that serves as the entry point for event discovery, featuring smart summary widgets and a clear event listing.

#### Scenario: Viewing the dashboard
- **WHEN** the user navigates to the root dashboard
- **THEN** the system displays "London AI Radar" as the app title with a London location badge, three summary widgets ("This Week", "This Month", "Next Up"), a list of highlights, and a single-column event list.

#### Scenario: Applying a filter
- **WHEN** the user selects a filter (e.g., "London Only" or "Machine Learning")
- **THEN** the system immediately updates the event list to show only matching events with a smooth transition animation.

### Requirement: Summary Widgets with Event Details

The system SHALL display three summary widgets at the top of the dashboard, each providing an actionable snapshot.

#### Scenario: Viewing "This Week" widget
- **WHEN** the user views the "This Week" widget
- **THEN** the widget displays the event count as the primary number, followed by a compact list of event titles (capped at 5, with "+N more" overflow) for events occurring within the next 7 days.

#### Scenario: Viewing "This Month" widget
- **WHEN** the user views the "This Month" widget
- **THEN** the widget displays the event count as the primary number, followed by a compact list of event titles (capped at 5, with "+N more" overflow) for events occurring in the current calendar month.

#### Scenario: Viewing "Next Up" widget
- **WHEN** the user views the "Next Up" widget
- **THEN** the widget shows the soonest future event with the highest score, displaying its title, date, and score badge. If no future events exist, it falls back to the highest-scored past event and is labeled "Top Event" instead.
- **AND** the score in the "Next Up" widget includes a ℹ️ icon that explains the scoring heuristic on hover.

### Requirement: London Location Badge

The system SHALL display a prominent location badge indicating that events are curated for London.

#### Scenario: Viewing the London badge
- **WHEN** the user views the dashboard or any page
- **THEN** a small location badge (e.g., "📍 London" or a pill with "London") appears in the app header or sidebar, clearly indicating the curated city.

### Requirement: App Identity

The system SHALL use "London AI Radar" as the application name throughout the UI.

#### Scenario: Displaying the app title
- **WHEN** the application loads
- **THEN** the sidebar displays "London AI Radar" as the title and "Live Events Radar" (or similar) as the subtitle.

#### Scenario: Page title
- **WHEN** the user views any page
- **THEN** the browser tab title and header reflect the "London AI Radar" branding.

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
- **THEN** the sidebar is expanded, and the dashboard uses a single-column layout with a preview panel for event details.

### Requirement: Slide-out Detail Panel
The system SHALL allow users to view deep-dive event details without navigating away from the current list or calendar view.

#### Scenario: Opening event details
- **WHEN** the user clicks an event card in the dashboard or timeline
- **THEN** a panel slides out from the right side of the screen, displaying the full event description, links, and scoring rationale.

#### Scenario: Closing the detail panel
- **WHEN** the user clicks the "Close" button or clicks outside the panel
- **THEN** the panel slides back to the right, returning the user to their exact previous scroll position in the main view.