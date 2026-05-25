## ADDED Requirements

### Requirement: Visitor can subscribe with their email
The system SHALL allow any visitor to submit their email address to receive event notifications. The system SHALL validate the email format and store the subscription.

#### Scenario: Successful subscription
- **WHEN** a visitor enters a valid email address and clicks "Subscribe"
- **THEN** the system stores the email in the `subscribers` table with `active = true` and returns a success message

#### Scenario: Duplicate email re-subscription
- **WHEN** a previously subscribed (or unsubscribed) email is submitted again
- **THEN** the system reactivates the existing subscription (sets `active = true`) and returns a success message

#### Scenario: Invalid email format
- **WHEN** a visitor enters an email that does not match a basic email pattern
- **THEN** the system returns a validation error and does not store the email

### Requirement: Visitor can unsubscribe with their email
The system SHALL allow any subscriber to remove themselves from the mailing list by submitting their email.

#### Scenario: Successful unsubscribe
- **WHEN** an active subscriber submits their email via the unsubscribe mechanism
- **THEN** the system sets their subscription `active = false` and returns a confirmation message

#### Scenario: Unsubscribe of unknown email
- **WHEN** an email that is not in the `subscribers` table is submitted for unsubscribe
- **THEN** the system returns a message indicating the email was not found

### Requirement: Frontend shows Subscribe button
The system SHALL display a "Subscribe to Updates" button in the sidebar of the single-page application.

#### Scenario: Subscribe button visible
- **WHEN** any user loads the frontend
- **THEN** they see a "Subscribe to Updates" button in the sidebar

#### Scenario: Subscribe modal opens on click
- **WHEN** a user clicks the "Subscribe to Updates" button
- **THEN** a modal appears with an email input field and a "Subscribe" action button

#### Scenario: Inline success message
- **WHEN** the subscription API call succeeds
- **THEN** the modal shows a success message and closes after a brief delay

#### Scenario: Inline error message
- **WHEN** the subscription API call fails (invalid email or server error)
- **THEN** the modal shows an error message and keeps the input open for correction

### Requirement: Batch notification to all subscribers
The system SHALL send a digest email to all active subscribers whenever new high-value events are discovered in a pipeline run. Multiple new events discovered in a single run SHALL be batched into one email.

#### Scenario: Single subscriber receives digest
- **WHEN** a pipeline run discovers new events with `score >= 7`
- **THEN** the system builds one digest email containing all new events and sends it to each active subscriber

#### Scenario: Multiple subscribers receive same digest
- **WHEN** there are multiple active subscribers
- **THEN** each subscriber receives the same digest email content

#### Scenario: No new events — no email sent
- **WHEN** a pipeline run discovers no new events with `score >= 7`
- **THEN** the system does not send any emails to subscribers

#### Scenario: Digest includes all new events batched together
- **WHEN** a pipeline run discovers 3 new high-value events
- **THEN** the single digest email contains all 3 events (not 3 separate emails)

### Requirement: Subscriber data is persisted
The system SHALL store subscriber data in a `subscribers` table in the existing SQLite database.

#### Scenario: Subscribers table exists after migration
- **WHEN** the database migration runs (via `migrate.py` or a new migration script)
- **THEN** a `subscribers` table exists with columns: `id` (INTEGER PRIMARY KEY), `email` (TEXT UNIQUE NOT NULL), `subscribed_at` (TIMESTAMP), `active` (INTEGER DEFAULT 1)

#### Scenario: Active subscriber query
- **WHEN** the notifier queries for subscribers
- **THEN** it only retrieves rows where `active = 1`