## ADDED Requirements

### Requirement: Extract location from event pages
The processor SHALL extract a `location` field from each event page, indicating the physical venue, city, or "Online" for virtual events.

#### Scenario: Event with venue in content
- **WHEN** the LLM processes a page that mentions a venue (e.g. "UCL, London" or "Seoul, South Korea")
- **THEN** the extracted event SHALL include a `location` field with that venue

#### Scenario: Online event
- **WHEN** the LLM processes a page for a virtual/online event
- **THEN** the extracted event SHALL include `location` set to "Online"

#### Scenario: No location found
- **WHEN** the LLM cannot determine a location from the page
- **THEN** the `location` field SHALL be null/empty

### Requirement: Store location in database
The events table SHALL have a `location` column to store the extracted location.

#### Scenario: Location persisted
- **WHEN** an event is inserted with a `location` value
- **THEN** that value SHALL be stored in the `location` column and returned by the API

### Requirement: Display location on event cards
The frontend SHALL show a location pill/badge on highlight cards and event list cards.

#### Scenario: London event card
- **WHEN** an event has `location` set to "London"
- **THEN** the card SHALL display "📍 London" as a small pill

#### Scenario: Online event card
- **WHEN** an event has `location` set to "Online"
- **THEN** the card SHALL display "🌐 Online" as a small pill

#### Scenario: Event with other location
- **WHEN** an event has `location` set to a specific venue/city
- **THEN** the card SHALL display that location as a text pill

#### Scenario: No location
- **WHEN** an event has no `location`
- **THEN** no location pill SHALL be shown