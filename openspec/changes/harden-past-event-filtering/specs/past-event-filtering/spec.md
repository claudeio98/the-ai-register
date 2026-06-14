# past-event-filtering Specification

## Purpose
Prevent past-dated events from being inserted into the database or included in email digests, while keeping existing past events available for Calendar browsing.

## ADDED Requirements

### Requirement: Processor skips past events
The processor SHALL check each event's date before inserting it and skip events whose date has already passed.

#### Scenario: Skip past-dated event during processing
- **WHEN** the processor extracts an event with a date that is before the current date
- **THEN** the processor SHALL NOT insert the event into the database
- **AND** the processor SHALL log "Skipping past event: <title> (date=<date>)"

#### Scenario: Process event with null date
- **WHEN** the processor extracts an event with no date field
- **THEN** the processor SHALL insert the event (cannot determine if it is past)

#### Scenario: Process today's event
- **WHEN** the processor extracts an event whose date is today
- **THEN** the processor SHALL insert the event (it is still relevant)

### Requirement: Notifier excludes past events
The notification system SHALL exclude events whose date has already passed from the email digest.

#### Scenario: Skip past event from digest at SQL level
- **WHEN** the notifier queries for high-value events to include in the digest
- **THEN** the SQL query SHALL include `WHERE date >= date('now')` to filter past events
- **AND** the Python `_is_future_date` fallback SHALL filter remaining non-ISO dates

#### Scenario: Include future events in digest
- **WHEN** the notifier generates a digest
- **THEN** all events with score >= 7, status = 'discovered', and date >= today SHALL be included
- **AND** events with a null date SHALL be included (cannot determine recency)

### Requirement: Past events remain in database
The filtering logic SHALL NOT delete or modify existing past events in the database — it only prevents new inserts / notifications.

#### Scenario: Past events preserved after filtering
- **WHEN** the pipeline processes and sends notifications
- **THEN** existing past-dated events SHALL remain in the `events` table with their current status