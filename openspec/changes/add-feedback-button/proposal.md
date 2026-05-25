## Why

The application currently lacks a direct way for users to provide feedback, report bugs, or suggest missing talks. This prevents the project from improving based on real-world usage and misses opportunities to expand the event database through community contributions.

## What Changes

- Add a "Feedback" button to the main user interface (Header/Navigation).
- Implement a feedback modal/form that allows users to select a category:
    - Bug Report
    - Missing Talk/Event
    - Feature Request
    - General Feedback
- Create a backend endpoint to process these submissions.
- Integrate a notification system (e.g., email via existing Gmail CLI or logging) to alert the maintainers of new submissions.

## Capabilities

### New Capabilities
- `feedback-submission`: Provides the UI and backend logic to capture and notify maintainers of user feedback, bug reports, feature requests, and missing talks.

### Modified Capabilities
- None

## Impact

- **Frontend**: New UI components for the feedback button and submission form.
- **Backend**: New API endpoint for receiving feedback payloads.
- **Infrastructure**: Use of the existing Gmail CLI or a similar mechanism to send notifications.
