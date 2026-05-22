## 1. Utility & Infrastructure

- [x] 1.1 Implement `normalizeDate` helper to ensure consistent `YYYY-MM-DD` formatting.
- [x] 1.2 Update `filteredEvents` computed property to support date-exact matches for the calendar.

## 2. Calendar Fixes

- [x] 2.1 Integrate `normalizeDate` into `getEventsForDate` to fix marker rendering.
- [x] 2.2 Implement `selectCalendarDate` to update the global `searchQuery` for view synchronization.

## 3. Intelligence Hub Redesign

- [x] 3.1 Create a "Top Highlights" computed property to extract the top 3 scored upcoming events.
- [x] 3.2 Implement the Dashboard "Summary Widgets" (Highlights Carousel, Quick Stats).
- [x] 3.3 Implement "Smart-Filter" shortcut buttons (This Week, Next Month).
- [x] 3.4 Ensure Dashboard highlight cards trigger the `selectedEvent` panel.

## 4. Polish & Verification

- [x] 4.1 Verify that clicking a calendar date filters both Dashboard and Timeline views.
- [x] 4.2 Test Calendar markers with various date formats to ensure robustness.
- [x] 4.3 Final UI polish for Dashboard widget spacing and responsiveness.
