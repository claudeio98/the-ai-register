## Why

Currently, the pipeline only sends high-value event digests to a single hardcoded Gmail address. There is no way for external users to subscribe to receive event notifications. Adding a public subscription system will make the AI Events Intelligence Pipeline useful as a shared service — anyone can sign up to receive batch email updates whenever new AI/ML events are discovered.

## What Changes

- **New `subscribers` database table**: Stores email addresses, subscription timestamps, and active status.
- **New API endpoint `POST /subscribe`**: Accepts an email address, validates it, stores it in the database.
- **New API endpoint `POST /unsubscribe`**: Accepts an email address or token to remove/disable a subscription.
- **Frontend "Subscribe to Updates" button**: A button in the UI that opens an email input form.
- **Updated notifier logic**: Instead of emailing only the hardcoded `GMAIL_USER`, the notifier queries all active subscribers and sends batch digests to each.
- **Batch email behavior**: If multiple new events are discovered in a single pipeline run, they are batched into one digest email per subscriber (not one email per event).
- **New backend script or migration**: Creates the `subscribers` table and migrates existing DB.

## Capabilities

### New Capabilities
- `email-subscription`: Public email subscription system — subscribe, unsubscribe, and receive batch notifications of newly discovered events.

### Modified Capabilities
<!-- No existing spec requirements are changing; the notifier behavior is an implementation detail of the existing notification pipeline. -->

## Impact

- **Database**: New `subscribers` table with columns `id`, `email` (unique), `subscribed_at`, `active` (boolean).
- **Backend API** (`src/api.py`): Add `POST /subscribe` and `POST /unsubscribe` endpoints.
- **Frontend** (`frontend/index.html`): Add "Subscribe to Updates" button and email input modal.
- **Notifier** (`src/notifier.py`): Rewrite to send digests to all active subscribers instead of a single hardcoded recipient.
- **Dependencies**: Uses existing `gmcli` tool for email sending (no new dependencies).
