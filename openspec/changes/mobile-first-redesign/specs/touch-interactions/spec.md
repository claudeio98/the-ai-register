## ADDED Requirements

### Requirement: Always-Visible Hide Button
On mobile viewports (< 768px), the event hide button SHALL be always visible with a minimum 44x44px tap target, regardless of hover or focus state.

#### Scenario: Hide button visible on mobile
- **WHEN** an event card is rendered on a mobile viewport
- **THEN** the hide button (×) SHALL be visible at all times with `opacity-100` and sufficient touch target size.

#### Scenario: Tapping hide button
- **WHEN** the user taps the hide button on an event card
- **THEN** the event is hidden and disappears from the list, matching the existing hide behavior.

### Requirement: Tap-to-Reveal Score Tooltip
On mobile viewports, score tooltips SHALL be revealed by tapping the ⓘ icon, toggling on tap and closing on a second tap or tapping outside.

#### Scenario: Tapping the score info icon
- **WHEN** the user taps the ⓘ icon next to a score badge
- **THEN** a tooltip appears explaining the score heuristic, and tapping again or tapping outside closes it.

### Requirement: Swipe-to-Dismiss Events
On mobile viewports, the user SHALL be able to swipe an event card left to reveal a hide action or dismiss it.

#### Scenario: Swiping event card
- **WHEN** the user swipes an event card leftward on mobile beyond a threshold (e.g., 80px)
- **THEN** the event is hidden and removed from the list.

#### Scenario: Canceling a swipe
- **WHEN** the user swipes an event card leftward but releases before the threshold
- **THEN** the card snaps back to its original position without hiding the event.

### Requirement: Pull-to-Refresh
On mobile viewports, pulling down from the top of the event list SHALL trigger a refresh of event data from the API.

#### Scenario: Pull-to-refresh gesture
- **WHEN** the user pulls down from the top of the event list (scrollTop === 0) past a 60px threshold
- **THEN** the system shows a loading indicator and calls the fetchEvents API to reload event data.

#### Scenario: Cancel pull-to-refresh
- **WHEN** the user pulls down but releases before the 60px threshold
- **THEN** the list snaps back without triggering a refresh.

### Requirement: Touch Active State
All interactive elements (buttons, cards, nav items) SHALL show a visual active/tap state on touch devices.

#### Scenario: Tap feedback on interactive elements
- **WHEN** the user touches a button or interactive element
- **THEN** the element SHALL show a visual feedback state (e.g., opacity change, scale transform, or background color change) while pressed.

