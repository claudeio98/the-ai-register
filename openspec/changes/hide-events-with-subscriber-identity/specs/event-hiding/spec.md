# event-hiding Specification

## Purpose
Allow subscribed users to hide events they are not interested in, with persistence tied to their subscriber email for cross-device sync.

## ADDED Requirements

### Requirement: Hide Event
The system SHALL allow a subscribed user to hide any visible event from all dashboard views.

#### Scenario: Hiding an event from the event list
- **WHEN** a subscribed user clicks the "Hide" button on an event card in the event list
- **THEN** the system SHALL send a POST request to `/events/{id}/hide` with the subscriber email header
- **THEN** the event SHALL be removed from the current view
- **THEN** the event SHALL remain hidden on page refresh and across devices using the same subscriber email

#### Scenario: Hiding an event from highlights
- **WHEN** a subscribed user clicks the "Hide" button on a highlight card
- **THEN** the system SHALL send a POST request to `/events/{id}/hide` with the subscriber email header
- **THEN** the highlight card SHALL disappear from the highlights section

#### Scenario: Hiding an event from the detail panel
- **WHEN** a subscribed user clicks the "Hide" button in the detail panel
- **THEN** the system SHALL hide the event and close the detail panel
- **THEN** the event card SHALL be removed from the underlying list view

### Requirement: Unhide Event
The system SHALL allow a subscribed user to restore a previously hidden event.

#### Scenario: Unhiding from Hidden Events management view
- **WHEN** a subscribed user opens the "Hidden Events" management view and clicks "Unhide" on a hidden event
- **THEN** the system SHALL send a POST request to `/events/{id}/unhide` with the subscriber email header
- **THEN** the event SHALL be removed from the hidden list
- **THEN** the event SHALL reappear in the main dashboard views on next refresh

### Requirement: Hidden Events Management View
The system SHALL provide a dedicated view where users can see all their hidden events and unhide them.

#### Scenario: Viewing hidden events
- **WHEN** a subscribed user clicks "Manage Hidden" in the sidebar
- **THEN** a slide-out panel SHALL display a list of all hidden events with title, date, and an "Unhide" button per event
- **THEN** if no events are hidden, the panel SHALL display "No hidden events"

### Requirement: Fetch Hidden State on Load
The system SHALL fetch the user's hidden event IDs when the app loads (if the user has a stored subscriber email).

#### Scenario: Loading hidden IDs on app bootstrap
- **WHEN** the app starts and a subscriber email is stored in localStorage
- **THEN** the system SHALL fetch the list of hidden event IDs from the backend (via `GET /events/hidden?subscriber_email=...`)
- **THEN** the system SHALL filter hidden events from all computed views

### Requirement: Unsubscribed User Prompt
The system SHALL prompt unsubscribed users to subscribe when they attempt to hide an event.

#### Scenario: Unsubscribed user clicks Hide
- **WHEN** an unsubscribed user clicks the "Hide" button on any event
- **THEN** the system SHALL display a prompt: "Subscribe to save your hidden events across devices. Enter your email to hide this event."
- **THEN** if the user enters a valid email and subscribes, the hide operation SHALL proceed
- **THEN** if the user dismisses the prompt, the hide operation SHALL be cancelled

### Requirement: Backend Persistence
The backend SHALL store hidden events in a `hidden_events` table keyed by subscriber email.

#### Scenario: Storing a hide
- **WHEN** the backend receives a POST to `/events/{id}/hide` with a valid subscriber_email header
- **THEN** the system SHALL insert a row into `hidden_events` with the event_id and subscriber_email
- **THEN** the system SHALL return HTTP 200 with `{"success": true}`
- **THEN** if the subscriber email is not active, the system SHALL return HTTP 403 with an error message

#### Scenario: Storing an unhide
- **WHEN** the backend receives a POST to `/events/{id}/unhide` with a valid subscriber_email header
- **THEN** the system SHALL delete the corresponding row from `hidden_events`
- **THEN** the system SHALL return HTTP 200 with `{"success": true}`

#### Scenario: Duplicate hide request
- **WHEN** the backend receives a POST to `/events/{id}/hide` for an already-hidden event
- **THEN** the system SHALL return HTTP 200 with `{"success": true, "already_hidden": true}`

### Requirement: Sidebar Restore Saved View Field
The system SHALL provide an inline "Restore Saved View" section in the sidebar that lets subscribed users enter their email to restore their hidden events state.

#### Scenario: Subscribed user restores on page load
- **WHEN** a subscribed user opens the app on a new device
- **THEN** the sidebar SHALL display a "Restore Saved View" heading with an email input and a "[Restore]" button, plus a small hint: "Enter your subscription email to sync your hidden events across devices."
- **WHEN** the user enters their valid subscription email and clicks Restore
- **THEN** the system SHALL validate the email against the subscribers table
- **THEN** the email SHALL be stored in localStorage
- **THEN** the system SHALL fetch hidden event IDs for that email
- **THEN** the sidebar SHALL update to show "✅ Restored (email@example.com)" with a "Clear" link

#### Scenario: Returning subscriber with localStorage email
- **WHEN** a user loads the app and has a stored subscriber email in localStorage
- **THEN** the system SHALL validate the stored email against the backend
- **THEN** if valid, the system SHALL fetch hidden IDs and apply filters automatically
- **THEN** the sidebar SHALL show "✅ Restored (email@example.com)" with a "Clear" link
- **THEN** if invalid (user unsubscribed), the system SHALL clear the stored email and show the Restore field

#### Scenario: Unsubscribed user enters email
- **WHEN** a non-subscriber enters an unregistered email in the Restore field
- **THEN** the system SHALL show an error: "No subscription found for this email. Subscribe below to get started."
- **THEN** the focus SHALL shift to the Subscribe button/modal

### Requirement: Filter Hidden Events from Listings
The GET `/events` endpoint SHALL exclude hidden events when a subscriber email is provided.

#### Scenario: Filtered listing
- **WHEN** a GET request to `/events` includes a `subscriber_email` query parameter with an active subscriber email
- **THEN** the response SHALL exclude any events that are in the `hidden_events` table for that email
- **THEN** if the subscriber email is empty or inactive, all events SHALL be returned unfiltered