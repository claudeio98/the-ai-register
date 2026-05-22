## Context

The app currently has three views (Dashboard, Timeline, Calendar) but the Timeline duplicates the Dashboard's event list. The Calendar dots don't provide enough context at a glance. The Dashboard is just a flat list.

## Goals / Non-Goals

**Goals:**
- Remove Timeline view and its navigation entry.
- Display event title + score inside each calendar cell on the right side.
- Add "This Week" and "Highlights" summary widgets to the Dashboard.
- Keep the two-view layout clean on mobile and desktop.

**Non-Goals:**
- No backend changes needed.
- No pagination changes.

## Decisions

### 1. Calendar cell layout
- **Decision**: Use a stacked layout inside each cell: day number on top-left, event title truncated below, score badge in small text.
- **Rationale**: Shows meaningful info without needing a hover/click interaction.
- **Alternative**: Tooltip on hover → rejected because mobile users can't hover.

### 2. Dashboard widgets
- **Decision**: Add a top row of stat cards: "This Week" count, "This Month" count, "Top Score". Below that, a "Highlights" section showing the top 3 scored upcoming events.
- **Rationale**: Provides immediate value and context.
- **Alternative**: Complex charts → rejected for simplicity.

### 3. Navigation simplification
- **Decision**: Remove Timeline from sidebar and bottom nav. Keep only Dashboard and Calendar.
- **Implementation**: Remove the button element and the `v-if` block for `view === 'timeline'`.

## Risks / Trade-offs

- **[Risk]** Calendar cells get cluttered with long event titles → **Mitigation**: Truncate titles with CSS `line-clamp` and set a max-height on the cell.
- **[Risk]** Removing Timeline loses chronological scroll view → **Mitigation**: The user requested it, and the Dashboard + Calendar cover the use case better.