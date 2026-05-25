## Context

The current frontend (`frontend/index.html`, ~810 lines) is a Vue 3 + Tailwind single-page app with desktop-first responsive patterns. On mobile (< 768px), the sidebar is completely hidden (`hidden md:flex`), replaced by a text-only bottom nav bar. Key features (Restore View, Manage Hidden, Subscribe, Feedback) are inaccessible or degraded. Event hide buttons require hover, score tooltips require hover, calendar cells are cramped, and the detail panel slides from the right rather than using mobile-native patterns.

This design covers a mobile-first overhaul of the existing single-file frontend. No API, backend, or dependency changes are needed.

## Goals / Non-Goals

**Goals:**
- Bottom navigation bar with icons replacing text-only mobile nav
- Hamburger/drawer menu exposing all sidebar features on mobile
- Bottom sheet for event details (replaces right-slide panel on mobile)
- Always-visible hide buttons on touch devices
- Tap-to-reveal score tooltips
- Pull-to-refresh gesture
- Compact event card layout (~30% vertical space reduction on mobile)
- Collapsible search bar (icon → expands)
- Calendar cells resized for small screens with abbreviated event display
- Bottom sheets for subscribe, feedback, hidden events panels on mobile
- Touch-active visual feedback on interactive elements

**Non-Goals:**
- No backend or API changes
- No data model changes
- No new external dependencies
- No PWA/service worker implementation
- No city selection UI (future feature)
- No tablet-specific breakpoint (phone-first, desktop uses existing layout)

## Decisions

### Decision: Bottom navigation with drawer pattern over hamburger-only

**Choice**: Bottom nav bar (Dashboard, Calendar, Search, Menu icons) + drawer overlay for sidebar features.

**Alternatives considered:**
- **Hamburger-only**: Single menu button in header. Higher tap friction — every sidebar action requires 2 taps (open menu, tap action).
- **Full sidebar on mobile**: Impractical — sidebar is 256px wide on a 375px screen, leaving almost no content area.
- **Bottom nav only (no drawer)**: Some features (Restore View, Manage Hidden) don't fit in a 4-tab nav.

**Rationale**: Bottom nav puts primary navigation within thumb reach. The Menu tab opens a drawer overlay exposing the full sidebar feature set (Restore View, Manage Hidden, Subscribe, Feedback). This is the standard mobile app pattern — 4-tab bottom nav with a "More" / hamburger entry point.

### Decision: Bottom sheet for event details over right-slide panel

**Choice**: On mobile (< 768px), event details slide up from the bottom as a draggable sheet. On desktop, keep the existing right-slide panel.

**Alternatives considered:**
- **Full-screen overlay**: More disruptive — hides the event list entirely.
- **Right-slide panel on mobile**: Works against mobile UX conventions; hard to reach the top of the panel one-handed.
- **Inline expansion**: Difficult to show all detail content without unnatural scrolling.

**Rationale**: Bottom sheets are the mobile OS standard for detail views. They're thumb-reachable, support natural swipe-to-dismiss, and preserve context by showing the event list behind the sheet's drag handle. Implementation uses fixed positioning with CSS `translateY` animation and a semi-transparent backdrop.

### Decision: Always-visible hide buttons and tap tooltips over hover-only

**Choice**: On mobile, hide buttons are always visible with `opacity-100` (minimum 44x44px tap target). Score tooltips use a tap-to-toggle pattern (click shows tooltip, click again or click outside hides it).

**Alternatives considered:**
- **Swipe-to-hide without visible button**: Discoverability problem — users won't know swipe works.
- **Long-press for tooltips**: Non-standard, slow.

**Rationale**: Touch devices have no hover state. Always-visible buttons solve the discoverability problem. Tap-to-toggle for tooltips matches mobile patterns (no hover) and avoids clutter by not showing all tooltips at once.

### Decision: Compact event card layout

**Choice**: On mobile, remove the w-12 h-12 date badge and show date inline. Reduce card padding from p-4 to p-3. Stack elements horizontally more efficiently.

**Desktop**: Keep the existing card layout with date badge.

**Rationale**: The date badge takes significant space and is redundant (date is shown as text below the title). Removing it on mobile saves ~30% vertical space, fitting more events above the fold.

### Decision: Collapsible search bar

**Choice**: On mobile, the search bar shows as a magnifying glass icon in the header. Tapping it expands to a full-width input. Tapping outside or pressing Escape collapses it back.

**Rationale**: Saves header real estate on small screens while keeping search accessible. Standard mobile pattern (most apps implement this).

### Decision: Pull-to-refresh via touch events

**Choice**: Use `touchstart`/`touchmove`/`touchend` event handlers on the main content area to detect pull-down gesture. Show a loading indicator (spinner or arrow) during the gesture.

**Alternatives considered:**
- **Library (e.g., vue-pull-to-refresh)**: Avoids adding dependencies.
- **Refresh button only**: Less discoverable, requires user to find the button.

**Rationale**: Pull-to-refresh is an expected mobile convention. Implementing with native touch events avoids new dependencies. The gesture triggers `fetchEvents()` after a threshold (e.g., 60px pull-down).

### Decision: Calendar cell responsive scaling

**Choice**: On mobile, calendar cells use `min-height: 4rem` (half the desktop 8rem). Each cell shows only score badges (no titles) unless the cell is tapped to expand. A "tap to expand" affordance shows "+N more" for cells with events.

**Rationale**: 7-column grids on 375px screens give ~50px per column. Showing event titles in each cell is impossible without illegible truncation. Score badges alone fit, and tapping the cell shows the day's events.

## Risks / Trade-offs

- **[Risk] Bottom sheet conflicts with existing panel transitions** → The current app uses `translateX(100%)` for all slide-in panels. Bottom sheets use `translateY(100%)`. We need to conditionally apply different transition classes based on viewport width. **Mitigation**: Use computed classes that switch between `slide-right` and `slide-up` variants based on a `isMobile` computed ref.

- **[Risk] Pull-to-refresh interferes with normal scrolling** → Pull-to-refresh activates only when scroll position is at the top (scrollTop === 0) and the user pulls down. **Mitigation**: Check `scrollTop === 0` before activating the gesture; cancel if user scrolls up during the pull.

- **[Risk] Adding touch-event handlers to all event cards causes performance issues with many events** → Each card needs touch handlers for swipe-to-hide. **Mitigation**: Use event delegation on the parent container rather than per-card listeners. Debounce touch move handlers.

- **[Trade-off] Bottom nav adds 64px of fixed height** → This reduces content area by 64px on mobile. The nav is essential for navigation, and 64px is the standard bottom nav height. Content uses the remaining space.

- **[Trade-off] Compact cards show less info per card** → Users see less text at a glance. The trade-off is more events visible simultaneously. Users can tap to open the detail panel for full information.

- **[Risk] Drawer menu conflicts with existing slide panels** → Both use absolute/fixed positioning. **Mitigation**: The drawer renders as a fixed overlay with its own z-index layer, separate from the detail/subscribe/feedback panels.