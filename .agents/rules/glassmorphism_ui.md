# Glassmorphism UI Constraints

When working on UI designs that heavily rely on Glassmorphism (e.g., `backdrop-filter: blur`), be aware of the CSS containing block behaviors that can cause coordinate drifting.

## The `position: fixed` Trap
When implementing tooltips or floating elements using `position: fixed` inside a UI heavily styled with Glassmorphism, the `backdrop-filter` creates a new containing block. This means the `fixed` positioning will be relative to the element with the `backdrop-filter`, not the viewport.

## The Fix
**Always** use React's `createPortal(..., document.body)` for elements that track `e.clientX` / `e.clientY` (like tooltips or custom context menus) to ensure they are rendered relative to the true viewport and do not get clipped or severely offset.
