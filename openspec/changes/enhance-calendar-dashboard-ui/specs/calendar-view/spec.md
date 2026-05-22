## MODIFIED Requirements

### Requirement: Calendar Cell Content
The system SHALL display truncated event titles and score badges inside each calendar cell, replacing simple dot markers.

#### Scene: Cell with multiple events
- **WHEN** a cell has 1 event
- **THEN** the cell SHALL show the event title (truncated) and score badge below the day number.
- **WHEN** a cell has 2 or more events
- **THEN** the cell SHALL show the first event title (truncated) and a "+N more" indicator.

#### Scene: Cell without events
- **WHEN** a calendar day has no events
- **THEN** only the day number SHALL be shown.