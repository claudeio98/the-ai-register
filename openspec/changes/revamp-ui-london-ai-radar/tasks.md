## 1. Rebrand to "London AI Radar"

- [x] 1.1 Update sidebar title from "AI Events" to "London AI Radar" and subtitle from "Intelligence Pipeline" to "Live Events Radar"
- [x] 1.2 Update `<title>` tag in `<head>` from "AI Events Tracker" to "London AI Radar"
- [x] 1.3 Add a London location badge (e.g., "📍 London" pill) in the sidebar header or next to the title

## 2. Replace Top Score with Next Up Widget

- [x] 2.1 Create a `nextUp` computed property that finds the soonest future event with the highest score (falling back to the highest-scored past event labeled "Top Event")
- [x] 2.2 Replace the "Top Score" summary card with a "Next Up" card showing the event title, date, and score badge
- [x] 2.3 Add ℹ️ icon next to the Next Up score with tooltip text on hover

## 3. Enhance This Week / This Month Widgets with Event Titles

- [x] 3.1 Create `thisWeekEvts` and `thisMonthEvts` computed properties returning the event objects (not just counts)
- [x] 3.2 Update the "This Week" card to show event count + compact list of event titles (capped at 5, with "+N more" overflow)
- [x] 3.3 Update the "This Month" card to show event count + compact list of event titles (capped at 5, with "+N more" overflow)

## 4. Switch Event List to Single-Column Layout

- [x] 4.1 Change event list grid from `grid-cols-1 lg:grid-cols-2` to `grid-cols-1` (single column)

## 5. Add Score Display to Calendar Cells

- [x] 5.1 Update calendar cell event rendering to include a color-coded score badge next to each event title
- [x] 5.2 Add ℹ️ tooltip icon to calendar score badges with hover explanation
- [x] 5.3 Adjust calendar cell styling to accommodate the score badge without breaking the compact layout

## 6. Add Score Annotation Tooltips

- [x] 6.1 Add a computed property or inline data for the tooltip text: "Scores (0–10) are AI-generated based on relevance, timeliness, and event prominence."
- [x] 6.2 Add ℹ️ icon next to score badges on event cards in the event list, with hover tooltip
- [x] 6.3 Add ℹ️ icon next to score badges on highlight cards
- [x] 6.4 Style the tooltip popover (white background, shadow, rounded, positioned above/below the icon)

## 7. Add Score Rationale in Detail Panel

- [x] 7.1 Add a "Why this score?" section in the side panel, below the score badge, showing the heuristic explanation text
- [x] 7.2 Style the section as an expandable/collapsible footnote or subtle descriptive line

## 8. Verification

- [x] 8.1 Load the app and confirm the sidebar shows "London AI Radar" with London badge
- [x] 8.2 Confirm "Next Up" widget shows the nearest high-scored future event (or fallback)
- [x] 8.3 Confirm "This Week" and "This Month" widgets show event titles below the count
- [x] 8.4 Confirm the event list is a single column
- [x] 8.5 Hover over ℹ️ icons on event cards, highlights, calendar, and Next Up — confirm tooltip appears
- [x] 8.6 Confirm score badges appear in calendar cells alongside event titles
- [x] 8.7 Confirm detail panel shows score rationale
- [x] 8.8 Run `python tests/test_*.py` to ensure no regressions