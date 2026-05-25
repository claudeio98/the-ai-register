## Context

The application provides a curated list of AI events and talks. Currently, there is no mechanism for users to notify the maintainer about errors, missing content, or general feedback. The goal is to add a lightweight feedback loop.

## Goals / Non-Goals

**Goals:**
- Provide a simple UI for users to send feedback.
- Categorize feedback (Bug, Missing Talk, Feature Request, General).
- Notify the maintainer via email/notification when feedback is received.
- Ensure the feedback submission is asynchronous and doesn't block the UI.

**Non-Goals:**
- Build a full-blown ticketing system with user accounts and status tracking.
- Provide a public feedback board.
- Real-time chat support.

## Decisions

- **UI Implementation**: Use a Vue 3 modal for the feedback form to avoid navigating away from the current page.
- **Backend Endpoint**: Create a POST `/api/feedback` endpoint in the FastAPI backend.
- **Notification Method**: Use the existing Gmail CLI integration (or a simple `smtplib` wrapper) to send an email to the project maintainer. For simplicity in the initial version, logging the feedback to a file or console in the backend is the primary fallback.
- **Data Storage**: Feedback will not be stored in the SQLite database in the first iteration to keep it simple; it will be forwarded immediately to the maintainer. If storage is needed later, a `feedback` table can be added.

## Risks / Trade-offs

- **Spam**: Since there is no authentication for feedback, the endpoint is vulnerable to spam. 
    - *Mitigation*: Implement a simple rate-limiting mechanism (e.g., based on IP address) or a basic honeypot field in the form.
- **Delivery Failure**: If the email notification fails, the feedback is lost.
    - *Mitigation*: Log the feedback to a local file on the server before attempting to send the notification.
