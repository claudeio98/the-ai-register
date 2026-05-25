## Context

The application currently displays a generic "AI Events" UI with a "Top Score" numeric widget that provides no actionable information, a two-column event grid that feels cluttered, and no indication that events are curated for London. The changes are purely frontend — `frontend/index.html` is the only file affected.

## Goals / Non-Goals

**Goals:**
- Replace the abstract "Top Score" widget with a "Next Up" card showing the nearest high-value event
- Add event titles below "This Week" / "This Month" counts
- Switch event listing from 2-column grid to single-column list for clarity
- Show event score alongside title in calendar cells
- Add a hover tooltip (ⓘ icon) explaining the score heuristic
- Display a "London" badge indicating the curated location
- Rename the app to "London AI Radar" throughout

**Non-Goals:**
- No API or backend changes
- No data model changes
- No city selection UI (future feature)
- No new dependencies
- No mobile-specific layout overhaul (existing responsive behavior is preserved)

## Decisions

### Decision: Single-column event list over 2-column grid
**Rationale**: The user reported the two-column layout is unclear. With varying event title lengths, score badges, institution names, and duplicate indicators, a single column gives each event full horizontal space and eliminates the "jagged" visual alignment that makes scanning harder.

### Decision: "Next Up" widget replaces "Top Score"
**Rationale**: "Top Score" showed a contextless number (e.g., "8.5 / 10"). "Next Up" selects the single future event with the highest score and shows its title, date, and score — giving the user an immediate, actionable next thing to look at. If no future events exist, it falls back to the highest-scored past event.

### Decision: Inline event titles under summary counts
**Rationale**: Rather than a separate section or modal, we render a compact list of event titles directly below "This Week" and "This Month" counts. This keeps the summary widget self-contained while satisfying the user's request to see *which* events are in those periods.

### Decision: ⓘ icon tooltip for score explanation
**Rationale**: A small question-mark / info icon next to score badges avoids permanently occupying space with explanatory text. On hover, a small popover explains that scores are AI-generated (0–10) based on relevance, timeliness, and prominence. The same explanation appears near the "Next Up" score.

### Decision: Static "London" badge in the header
**Rationale**: All current events are London-based. Rather than hiding this, we surface it as a small location badge in the app header. The badge is purely presentational now but could become a city selector dropdown in the future.

## Risks / Trade-offs

- **[Risk] Event list becomes too long vertically** → Mitigation: The search filter at the top still works, and we can add a "Show more / Show less" toggle if needed. Single column at ~100px height per card means ~10 cards fit without scroll on desktop.
- **[Risk] "Next Up" selects a past event if no future events exist** → This is intentional as a graceful fallback, but the widget should still label it clearly. Mitigation: prefix text changes from "Next Up" to "Top Event" when falling back to past events.
- **[Trade-off] Inline event titles in summary widgets add vertical space** → The lists are capped at 5 titles with a "+N more" overflow, keeping the widgets compact.