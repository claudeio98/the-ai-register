## ADDED Requirements

### Requirement: Bottom Navigation Bar
The system SHALL provide a fixed bottom navigation bar on mobile viewports (< 768px) with icon-labeled tabs for primary actions.

#### Scenario: Navigating via bottom tabs
- **WHEN** the user taps a tab in the bottom navigation bar
- **THEN** the system switches to the corresponding view (Dashboard or Calendar) and highlights the active tab with the primary color.

#### Scenario: Opening the drawer menu
- **WHEN** the user taps the Menu icon in the bottom navigation bar
- **THEN** the system opens a drawer overlay from the left side of the screen containing: Restore Saved View section, Manage Hidden button, Subscribe button, and Feedback button.

### Requirement: Drawer Menu
The system SHALL provide a slide-in drawer menu from the left on mobile that surfaces all features currently in the desktop sidebar.

#### Scenario: Opening the drawer
- **WHEN** the user taps the Menu tab
- **THEN** the drawer slides in from the left, displaying the app title, London badge, and all sidebar actions (Restore View, Manage Hidden, Subscribe, Feedback).

#### Scenario: Closing the drawer
- **WHEN** the user taps the close button, taps outside the drawer, or taps a navigation action
- **THEN** the drawer slides back to the left and is hidden.

#### Scenario: Restoring view from drawer
- **WHEN** the user enters an email in the Restore Saved View section within the drawer and taps "Restore"
- **THEN** the system restores their hidden events and the drawer closes.

### Requirement: Mobile Navigation Icons
The bottom navigation tabs SHALL display descriptive icons alongside text labels for quick visual recognition.

#### Scenario: Icon display
- **WHEN** the bottom navigation bar is rendered
- **THEN** each tab SHALL display an icon (using Unicode or inline SVG) and a text label below it.

