## Why

The current "Smart Calendar" implementation has a redundant Dashboard view that mimics a simple list, and the Calendar view fails to correctly render event markers due to strict date matching. To truly live up to the "Smart" label, the Dashboard needs to transition from a list to an Intelligence Hub, and the Calendar requires a robust date-handling mechanism.

## What Changes

- **Dashboard Transformation**: Replace the event list in the Dashboard with an "Intelligence Hub" featuring summary widgets (e.g., "Upcoming Highlights", "Top-Scored Events", "Discovery Stats").
- **Calendar Fix**: Implement a more flexible date-matching algorithm to ensure event markers appear correctly regardless of minor string formatting differences.
- **Enhanced Calendar UX**: Add a "Quick-Jump" to event functionality when clicking a date in the calendar.
- **Unified Search Refinement**: Ensure that search queries seamlessly update all views, including the new Dashboard widgets.

## Capabilities

### New Capabilities
- `intelligence-hub`: A summary-driven dashboard providing high-level insights and curated highlights.

### Modified Capabilities
- `calendar-view`: Fix date matching and implement date-to-event navigation.
- `event-dashboard`: Redesign from a list view to a widget-based intelligence hub.

## Impact

- **Frontend**: Modification of `frontend/index.html` Vue logic and templates.
- **Logic**: Update to the `getEventsForDate` and `filteredEvents` computed properties.
