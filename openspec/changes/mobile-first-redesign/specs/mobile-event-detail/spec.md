## ADDED Requirements

### Requirement: Bottom Sheet Detail Panel
On mobile viewports (< 768px), the event detail panel SHALL slide up from the bottom of the screen as a draggable sheet rather than sliding from the right.

#### Scenario: Opening bottom sheet
- **WHEN** the user taps an event card on mobile
- **THEN** the detail panel slides up from the bottom with a drag handle at the top, showing event title, date, location, score, description, and action buttons.

#### Scenario: Dismissing with drag
- **WHEN** the user drags the sheet downward past a threshold (e.g., 30% of sheet height)
- **THEN** the sheet animates back down and closes, returning the user to the previous view.

#### Scenario: Tapping backdrop to dismiss
- **WHEN** the bottom sheet is open and the user taps the semi-transparent backdrop behind it
- **THEN** the sheet closes.

#### Scenario: Desktop retains right-slide panel
- **WHEN** the viewport width is 768px or greater
- **THEN** the detail panel continues to slide from the right, maintaining the existing desktop behavior.

### Requirement: Bottom Sheet Subscribe Panel
On mobile viewports, the subscribe modal SHALL slide up as a bottom sheet.

#### Scenario: Opening subscribe as bottom sheet
- **WHEN** the user taps "Subscribe" on mobile
- **THEN** the subscription form slides up from the bottom with the same content as the desktop slide-in panel.

### Requirement: Bottom Sheet Feedback Panel
On mobile viewports, the feedback modal SHALL slide up as a bottom sheet.

#### Scenario: Opening feedback as bottom sheet
- **WHEN** the user taps "Feedback" on mobile
- **THEN** the feedback form slides up from the bottom with the same content as the desktop slide-in panel.

### Requirement: Bottom Sheet Hidden Events Panel
On mobile viewports, the hidden events management panel SHALL slide up as a bottom sheet.

#### Scenario: Opening hidden events as bottom sheet
- **WHEN** the user taps "Manage Hidden" on mobile
- **THEN** the hidden events list slides up from the bottom.

