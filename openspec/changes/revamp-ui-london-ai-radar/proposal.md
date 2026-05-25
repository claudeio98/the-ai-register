## Why

The current UI feels generic and unclear. The "Top Score" box shows a bare number with no actionable value, the two-column event layout makes scanning difficult, and there's no indication that all events are London-focused. The app needs a more informative, distinctive identity that conveys its purpose at a glance.

## What Changes

- **App renamed** to **"London AI Radar"** with new subtitle — gives the app a clear, local identity
- **Top Score widget replaced** with **"Next Up"** — shows the single nearest high-value event with date and score (actionable vs. abstract)
- **This Week / This Month widgets enhanced** — event titles listed below the count so users see *which* events are upcoming
- **Event list layout** changes from 2-column grid to a single-column list for clearer scanning
- **Calendar cells** show both event title **and score** (currently only title)
- **Score tooltip** added — a small help icon (ℹ️ / ⓘ) on score badges that explains the heuristic on hover
- **London location badge** displayed prominently — shows "London" as the curated city (future-proofed for city selection)
- **Consistent naming** throughout the UI — sidebar, header, page title all use "London AI Radar"

## Capabilities

### New Capabilities
- `score-annotation`: Interactive tooltip/help that explains the relevance score heuristic (how scores are calculated, what "Top Score" means) when the user hovers over an info icon

### Modified Capabilities
- `event-dashboard`: Top Score widget replaced with Next Up; This Week / This Month widgets now list event titles below the count; dashboard shows a London location badge; app title/identity updated
- `calendar-view`: Calendar cells show both event title and score badge
- `event-listing`: Event list switches from 2-column grid to single-column list for clearer readability

## Impact

- **Frontend only** — `frontend/index.html` is the only file modified
- No API changes needed
- No new dependencies
- All changes are presentational / UX — no data model changes