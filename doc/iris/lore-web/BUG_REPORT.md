# Bug Report: Relations Graph Missing & Unstyled Content

**Status**: CRITICAL
**Component**: Lore Web (Relations Section)
**Date**: 2025-12-15
**Reported By**: User / AI Assistant

## Description
The "Relations" (Vztahy) section of the Lore Web application is failing to render correctly.
1.  **Graph Missing**: The force-directed graph canvas is blank or absent.
2.  **Unstyled Table**: The relations list below the graph appears as an unformatted table, indicating CSS classes are not being applied or the table structure is malformed at runtime.

## Steps to Reproduce
1.  Open `doc/iris/lore-web/index.html`.
2.  Navigate to the **Vztahy** (Relations) section via the main menu.
3.  Observe the empty space where the graph should be.
4.  Observe the list of relations below.

## Expected Behavior
-   A force-directed graph should appear, showing nodes for Admins (Top), Agents (Bottom Left), and Users (Bottom Right).
-   Hovering over nodes/links should show tooltips.
-   The relations list should be a styled data table (dark theme, borders, colored badges).

## Actual Behavior
-   Graph container is empty or canvas is blank.
-   Relations list renders but lacks styling (looks like a default HTML table).
-   User reports "Pořád to tam nevidím" (Still don't see it) despite cache busting attempts.

## Investigation & Fixes Applied
The following fixes were deployed but failed to resolve the issue for the user:

1.  **Code Corruption Fix (`graph.js`)**:
    -   Found critical corruption where `distToSegment` contained color codes and `getLinkColor` was missing.
    -   **Action**: Restored correct logic and added missing function. Verified syntax is now valid.

2.  **Missing Helpers (`app.js`)**:
    -   Found that `renderRelationsList` depended on `getRoleName` which was undefined.
    -   **Action**: Implemented `getRoleName` and `getRelTypeLabel` in `app.js`.

3.  **Layout Logic**:
    -   Updated `graph.js` to strictly position Admins at the top (25%) and others at the bottom (75%) with increased spacing.

4.  **Cache Busting**:
    -   Updated `index.html` to include `?v=20251215_fix3` on `style.css`, `graph.js`, and `app.js`.

5.  **CSS Verification**:
    -   Verified `style.css` contains correct `.data-table` definitions (lines 550-600).

## Potential Causes
1.  **Browser Caching (File Protocol)**: Browsers are extremely aggressive with caching local files (`file://`). Even with query parameters, Chrome/Firefox sometimes ignore them for local resources.
2.  **Runtime Error**: A silent runtime error in `RelationGraph` constructor might be aborting execution before drawing.
3.  **CSS Loading**: If the CSS file itself is cached or blocked (CORS?), the table styles won't apply.

## Recommended Next Steps
1.  **Hard Refresh**: Clear browser cache explicitly (Ctrl+F5 or settings).
2.  **Console Inspection**: Check browser DevTools console (F12) for "ReferenceError" or "SyntaxError".
3.  **Local Server**: Run the `lore-web` via a local HTTP server instead of `file://` to ensure proper resource loading and caching behavior.
