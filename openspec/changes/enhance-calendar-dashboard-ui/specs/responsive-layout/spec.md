## MODIFIED Requirements

### Requirement: Navigation
The system SHALL provide navigation exclusively between two views: Dashboard and Calendar.

#### Scenario: Simplified navigation
- **WHEN** the sidebar or mobile bottom nav is displayed
- **THEN** only "Dashboard" and "Calendar" buttons SHALL be shown.
- **THEN** the Timeline view SHALL no longer be accessible.

### Requirement: Adaptive UI Components
The system SHALL update the responsive layout to only render the Dashboard and Calendar views.

#### Scenario: View switching
- **WHEN** the user clicks "Calendar" in the sidebar or bottom nav
- **THEN** the Calendar view SHALL render.
- **WHEN** the user clicks "Dashboard"
- **THEN** the Dashboard view SHALL render.