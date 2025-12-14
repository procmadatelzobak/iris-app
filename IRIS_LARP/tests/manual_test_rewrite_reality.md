
# Manual Test: Fix Rewrite Reality Mode

1.  **Login as Admin:**
    -   Go to `/` and login as an admin (not root, or check if root uses dashboard.html).
    -   (If root uses `root_dashboard.html`, this fix applies to `dashboard.html` / standard admin).

2.  **Navigate to Station:**
    -   Click on any station (e.g. "UMYVADLO" - Monitoring).
    -   This opens the station view and shows the top nav bar.

3.  **Test Toggle (Fix 1):**
    -   Click "PŘEPSAT REALITU".
    -   Verify: Toast message "EDIT MODE ENGAGED" appears (instead of alert).
    -   Verify: Editable texts have dashed borders.
    -   Click "PŘEPSAT REALITU" again.
    -   Verify: Mode turns OFF (borders disappear, "EDIT MODE SAVED" toast).
    -   *Pass if it toggles on and off correctly.*

4.  **Test Navigation Auto-Off (Fix 2):**
    -   Click "PŘEPSAT REALITU" (Mode ON).
    -   Click "[ X ]" to close station OR click "ODHLÁSIT" (though logout reloads page so it resets anyway).
    -   Better test: Click "PŘEPSAT REALITU" (ON), then if there were other navigation buttons (like switching tabs in Monitor), check if it persists.
    -   Actually, the user request "přechodem na jinou stránku" implies navigating between stations.
    -   Try: Open Station -> Mode ON -> Click Close Station ([X]).
    -   Re-open Station. Verify: Edit mode should be OFF.

5.  **Success Criteria:**
    -   Button toggles mode reliably.
    -   Navigating away disables mode automatically.
