## Context

The AI Events Intelligence Pipeline currently uses a functional but basic Vue.js and Tailwind CSS frontend. The goal is to transform this into a "Smart Calendar" inspired experience that prioritizes visual clarity and reduced stress for the user when managing high-volume AI event data.

## Goals / Non-Goals

**Goals:**
- Implement a visually polished dashboard with a "clean" aesthetic (inspired by the provided Muzli example).
- Create a visual timeline/calendar view to organize events temporally.
- Develop a fully responsive layout that works seamlessly on mobile (stacked views) and desktop (multi-pane views).
- Implement a detail panel that allows users to inspect events without losing their place in the main list or calendar.
- Enhance the visual representation of "Event Scores" to make high-value events immediately apparent.

**Non-Goals:**
- Re-writing the entire backend API (only minor adjustments for date filtering).
- Adding a full-fledged Google Calendar synchronization (focus is on internal visualization).
- Changing the core event discovery logic.

## Decisions

### 1. Layout Architecture: Fluid Grid & Adaptive Panes
- **Decision**: Use a "Shell" approach where the main navigation is a collapsible sidebar on desktop and a bottom-bar/hamburger menu on mobile.
- **Rationale**: This maximizes screen real estate for the event content while ensuring critical navigation is always accessible.
- **Alternative**: Fixed top navigation. Rejected because it limits vertical space for the calendar/timeline view.

### 2. Visualization: The "Smart" Timeline
- **Decision**: Implement a vertical timeline view as the primary discovery mechanism, supplemented by a traditional monthly calendar view.
- **Rationale**: A vertical timeline is more intuitive for "scrolling through the future" and fits mobile screens better than a grid-based monthly calendar.
- **Alternative**: Monthly grid only. Rejected as it becomes cluttered with many events on a single day.

### 3. Component Strategy: Atomic Design
- **Decision**: Use an atomic design approach for UI components (e.g., `EventCard`, `ScoreBadge`, `TimelineItem`).
- **Rationale**: Ensures consistency across different views (Dashboard, Calendar, Details) and makes the responsive redesign easier to manage.
- **Alternative**: Page-specific large components. Rejected as it leads to code duplication.

### 4. User Interaction: Slide-over Detail Panel
- **Decision**: Use a right-side slide-over panel for event details.
- **Rationale**: Maintains the user's context in the main list/calendar, reducing the "pogo-sticking" effect (going back and forth between pages).
- **Alternative**: Modal pop-ups. Rejected as they block the entire view and feel more disruptive.

## Risks / Trade-offs

- **[Risk]** Complex CSS for the timeline view on mobile $\rightarrow$ **Mitigation**: Use Tailwind's flexible grid and flexbox, and test specifically on small viewports early.
- **[Risk]** Performance issues when rendering many event cards $\rightarrow$ **Mitigation**: Implement virtual scrolling or pagination for the event list/timeline.
- **[Risk]** Visual clutter if too many events overlap in the timeline $\rightarrow$ **Mitigation**: Implement "smart grouping" or "clustering" for events occurring on the same day.
