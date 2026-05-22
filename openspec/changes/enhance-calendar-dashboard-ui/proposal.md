## Why

The current UI has a redundant Timeline tab, a Calendar that only shows dots without any event context, and a Dashboard that is just a basic event list. To improve usability and make the app feel smarter, the Calendar needs inline event previews, the Timeline should be removed in favor of a simpler two-view app, and the Dashboard needs informative widgets.

## What Changes

- **Remove Timeline tab**: Delete the Timeline view and navigation entry. **BREAKING**
- **Calendar event previews**: Show event title and score directly inside each calendar cell, replacing the simple dots.
- **Dashboard intelligence**: Add "This Week", "Highlights", and "Monthly Stats" summary widgets.
- **Simplified navigation**: Keep only Dashboard and Calendar in the sidebar and bottom nav.

## Capabilities

### New Capabilities
- `calendar-previews`: Inline event title and score display within calendar grid cells.
- `dashboard-widgets`: Summary widgets for the Dashboard (This Week, Highlights, Stats).

### Modified Capabilities
- `responsive-layout`: Update navigation to exclude Timeline view.
- `calendar-view`: Replace marker dots with previews.

## Impact

- **Frontend**: Major edits to `frontend/index.html` Vue template and logic.
- **Navigation**: Removal of Timeline from sidebar and mobile bottom nav.