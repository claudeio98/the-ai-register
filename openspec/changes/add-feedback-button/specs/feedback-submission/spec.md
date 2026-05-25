## ADDED Requirements

### Requirement: Feedback Submission Form
The system SHALL provide a user interface for submitting feedback, including a category selection and a text area for the message.

#### Scenario: Successful submission
- **WHEN** a user fills out the form with a category (e.g., "Bug Report", "Feature Request") and a message, then clicks "Submit"
- **THEN** the system displays a success message and closes the modal.

#### Scenario: Validation error
- **WHEN** a user clicks "Submit" without filling in the message
- **THEN** the system displays a validation error stating that the message is required.

### Requirement: Feedback API Endpoint
The system SHALL provide a backend endpoint to receive and process feedback submissions.

#### Scenario: Successful API call
- **WHEN** a valid JSON payload with `category` and `message` is sent to `/api/feedback`
- **THEN** the system returns a 200 OK response and triggers the notification mechanism.

#### Scenario: Invalid API call
- **WHEN** a payload missing required fields is sent to `/api/feedback`
- **THEN** the system returns a 400 Bad Request response.

### Requirement: Maintainer Notification
The system SHALL notify the maintainer whenever new feedback is received.

#### Scenario: Email notification sent
- **WHEN** the backend successfully processes a feedback submission
- **THEN** an email is sent to the project maintainer containing the category and message.

#### Scenario: Notification failure fallback
- **WHEN** the email notification fails
- **THEN** the system logs the feedback details to a local file on the server.
