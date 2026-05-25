## Why

The current UI collapses to a bare-bones mobile experience: the sidebar (with Restore View, Manage Hidden, Subscribe, and Feedback) is entirely hidden, event hide buttons are hover-only (impossible on touch), calendar cells are illegibly cramped at `min-height: 8rem` across 7 columns, and the detail panel slides from the right instead of using a touch-native bottom sheet. Users on phones have a degraded experience that hides key features and makes common actions (hiding events, reading tooltips, accessing subscriptions) difficult or impossible.

## What Changes

- **Bottom navigation bar** replaces the current text-only mobile nav — adds icons for Dashboard, Calendar, Search, and Menu
- **Hamburger / drawer menu** on mobile to surface all sidebar features (Restore View, Manage Hidden, Subscribe, Feedback) that are currently hidden
- **Bottom sheet for event details** replaces the right-sliding panel on mobile (slides up from bottom, touch-dismissible)
- **Touch-optimized event cards**: hide buttons always visible, score tooltips tap-to-reveal, swipe-to-dismiss events
- **Compact event card layout** reducing vertical space per card by ~30%
- **Collapsible search bar** — collapses to an icon in the header on mobile, expands on tap
- **Calendar cells resized and restructured for small screens** — smaller cells, abbreviated event display, tap to expand
- **Detail panels (subscribe, feedback, hidden events) use bottom sheets on mobile** instead of right-sliding panels
- **Pull-to-refresh** gesture to reload event data
- **Score tooltip tap-to-reveal** pattern replaces hover-only tooltip
- **Active/tap state visual feedback** on buttons and interactive elements

## Capabilities

### New Capabilities
- `mobile-navigation`: Bottom nav bar with icons and a hamburger/drawer menu that surfaces all sidebar features (Restore View, Manage Hidden, Subscribe, Feedback) on mobile
- `mobile-event-detail`: Bottom sheet UI for event details on mobile, with touch-dismiss, swipe, and compact layout
- `touch-interactions`: Always-visible hide buttons, tap-to-reveal tooltips, swipe-to-dismiss events, pull-to-refresh, and active tap state feedback

### Modified Capabilities
- `event-dashboard`: Dashboard layout adapted for mobile — collapsible search bar, compact summary widgets, touch-optimized interaction patterns
- `event-listing`: Event cards redesigned for mobile — compact layout with ~30% less vertical space, always-visible hide button, swipe-to-dismiss
- `calendar-view`: Calendar view reworked for small screens — smaller cells with abbreviated event display, tap-to-expand cell details, mobile-friendly navigation
- `event-detail-panel`: Detail panel switches from right-slide to bottom-sheet pattern on mobile, adapted layout for small screens

## Impact

- **Frontend only** — `frontend/index.html` is the only file modified
- No API changes needed
- No new external dependencies (still Vue 3 + Tailwind CDN)
- CSS additions for bottom sheet animations, swipe gestures, pull-to-refresh
- Vue reactivity additions for mobile-specific state (drawer open, search expanded, touch actions)