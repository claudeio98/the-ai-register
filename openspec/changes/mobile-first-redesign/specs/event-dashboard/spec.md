## MODIFIED Requirements

### Requirement: Responsive Layout Framework
The system SHALL implement a fluid layout that adapts the UI based on the viewport size to ensure a consistent experience on mobile and desktop.

#### Scenario: Mobile View
- **WHEN** the viewport width is less than 768px
- **THEN** the sidebar collapses into a drawer accessible via the bottom navigation bar's Menu tab, event cards use a compact layout, search collapses to an icon, and all detail panels use bottom sheets instead of right-sliding panels.

#### Scenario: Desktop View
- **WHEN** the viewport width is 768px or greater
- **THEN** the sidebar is expanded, and the dashboard uses a multi-column grid to display events and the existing right-slide detail panel.

### Requirement: Collapsible Search Bar
The system SHALL provide a collapsible search bar on mobile that conserves header space.

#### Scenario: Search collapsed on mobile
- **WHEN** the viewport is less than 768px and search is not active
- **THEN** the search bar SHALL display as a magnifying glass icon in the header.

#### Scenario: Search expanded on mobile
- **WHEN** the user taps the search icon on mobile
- **THEN** the search input expands to full width with a smooth animation, gains focus, and the keyboard appears.

#### Scenario: Search collapsed on desktop
- **WHEN** the viewport is 768px or greater
- **THEN** the search bar SHALL display as a full-width text input, matching the current desktop behavior.

### Requirement: Compact Summary Widgets on Mobile
The dashboard summary widgets (This Week, This Month) SHALL use a more compact layout on mobile.

#### Scenario: Mobile summary widgets
- **WHEN** the viewport is less than 768px
- **THEN** the summary widgets SHALL use reduced padding and font sizes to fit more content above the fold.

