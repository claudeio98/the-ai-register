## 1. Foundation: Mobile Detection & Responsive Infrastructure

- [x] 1.1 Add `isMobile` computed ref based on `window.innerWidth < 768` with a `resize` event listener
- [x] 1.2 Create responsive CSS classes for bottom sheet transitions (`slide-up-enter-active`, `slide-up-leave-active`, `translateY` animations)
- [x] 1.3 Create responsive CSS classes for drawer menu transitions (`drawer-enter-active`, `drawer-leave-active`, `translateX` from left)
- [x] 1.4 Add backdrop overlay CSS (semi-transparent `bg-black/30` behind drawers and bottom sheets)
- [x] 1.5 Add CSS for pull-to-refresh indicator (spinner with pull-down offset)
- [x] 1.6 Add CSS for touch active states on interactive elements

## 2. Bottom Navigation Bar

- [x] 2.1 Replace the existing text-only mobile nav (`<nav class="md:hidden h-16...">`) with an icon + label bottom bar containing: Dashboard (🏠), Calendar (📅), Search (🔍), Menu (☰)
- [x] 2.2 Add active tab highlighting with the primary color for the current view
- [x] 2.3 Wire up Dashboard and Calendar tabs to switch `view` ref
- [x] 2.4 Wire up Search tab to toggle search expanded state
- [x] 2.5 Wire up Menu tab to open the drawer overlay
- [x] 2.6 Ensure the bottom nav is `fixed` at the bottom with proper z-index

## 3. Drawer Menu

- [x] 3.1 Create `showDrawer` ref and wire to Menu tab tap
- [x] 3.2 Build drawer overlay: fixed left panel (w-64), backdrop, close button
- [x] 3.3 Populate drawer with: app title + London badge, Restore Saved View section (email input + restore button), Manage Hidden button, Subscribe button, Feedback button
- [x] 3.4 Add slide-left animation for drawer open/close
- [x] 3.5 Add backdrop tap to dismiss
- [x] 3.6 Add close-on-action behavior (tapping any action closes the drawer)

## 4. Bottom Sheet Pattern

- [x] 4.1 Create a reusable bottom sheet wrapper using `<transition>` with `slide-up` CSS classes
- [x] 4.2 Implement drag-to-dismiss: track touch start Y, touch move delta, close on threshold or quick flick
- [x] 4.3 Add drag handle visual at top of sheet (horizontal bar)
- [x] 4.4 Add backdrop behind bottom sheet (tappable to dismiss)
- [x] 4.5 Conditionally apply `slide-up` vs `slide-right` transitions based on `isMobile` ref

## 5. Event Detail Bottom Sheet

- [x] 5.1 On mobile, render event detail panel as a bottom sheet (slides up) instead of right-slide panel
- [x] 5.2 On desktop, keep the existing right-slide panel behavior
- [x] 5.3 Ensure all detail content renders correctly in bottom sheet (title, score with tap tooltip, date, location, description, sources, action buttons)
- [x] 5.4 Add drag-to-dismiss and backdrop-tap-to-dismiss to the detail bottom sheet

## 6. Compact Event Cards on Mobile

- [x] 6.1 On mobile, remove the w-12 h-12 date badge from event cards — show date as inline text
- [x] 6.2 Reduce card padding from `p-4` to `p-3` on mobile
- [x] 6.3 Adjust the flex layout for mobile: compact title row with score, date line below
- [x] 6.4 Ensure duplicate count badge still displays on mobile
- [x] 6.5 On desktop, keep existing card layout unchanged

## 7. Touch Interactions

- [x] 7.1 Make hide button (×) always visible on mobile (`opacity-100`, remove `group-hover` dependency)
- [x] 7.2 Ensure hide button has minimum 44x44px tap target on mobile
- [x] 7.3 Implement tap-to-reveal score tooltips: toggle tooltip on click/tap, close on second tap or outside click
- [x] 7.4 Implement swipe-to-dismiss: touch event listeners on event cards, track swipe delta, hide on threshold
- [x] 7.5 Implement pull-to-refresh: touchstart/touchmove/touchend handlers on main content, check scrollTop === 0, trigger fetchEvents on 60px threshold with visual indicator
- [x] 7.6 Add `touch-active` CSS class via `@touchstart`/`@touchend` on interactive elements for visual press feedback

## 8. Collapsible Search Bar

- [x] 8.1 Add `searchExpanded` ref for mobile search state
- [x] 8.2 On mobile, render search as a magnifying glass icon in the header when collapsed
- [x] 8.3 On icon tap, expand search input to full width with focus
- [x] 8.4 On blur or Escape key, collapse search back to icon
- [x] 8.5 On desktop, keep full-width search bar as-is

## 9. Calendar Responsive

- [x] 9.1 Reduce `cal-cell` min-height from `8rem` to `4rem` on mobile
- [x] 9.2 On mobile cells, show only score badges per event (no titles)
- [x] 9.3 Add "+N more" overflow indicator for cells with >3 events
- [x] 9.4 Ensure tap-to-view-day behavior works on mobile cells
- [x] 9.5 On desktop, keep existing calendar cell layout unchanged

## 10. Convert Other Panels to Bottom Sheets on Mobile

- [x] 10.1 Subscribe modal: use bottom sheet on mobile (slide-up), keep right-slide on desktop
- [x] 10.2 Feedback modal: use bottom sheet on mobile (slide-up), keep right-slide on desktop
- [x] 10.3 Hidden events panel: use bottom sheet on mobile (slide-up), keep right-slide on desktop
- [x] 10.4 Ensure all converted panels maintain their existing content and functionality

## 11. Polish & Integration

- [x] 11.1 Add `active` state transitions to all buttons and cards (opacity/scale on press)
- [x] 11.2 Ensure smooth transitions when switching between mobile and desktop layouts (resize handling)
- [x] 11.3 Test all touch interactions on actual mobile device or Chrome DevTools device emulation
- [x] 11.4 Verify existing desktop layout is completely unaffected (no regressions above 768px)
- [x] 11.5 Verify sidebar features are accessible via drawer menu on mobile
- [x] 11.6 Remove any unused CSS or dead code from the changes
