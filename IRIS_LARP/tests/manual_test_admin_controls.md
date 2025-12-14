
# Manual Test: Admin Dashboard Controls

1.  **Login as Admin:**
    -   Go to `/` and login.
    -   Open Hub -> "ROZKOŠ" (Controls).

2.  **Test Stress Level Slider:**
    -   Drag the "HLADINA STRESU" (red) slider.
    -   Verify: The number in the center of the bar updates *while dragging* (Real-time).
    -   Verify: The "Manual Check" label updates.

3.  **Test Mode Switches:**
    -   Click "ÚSPORA" (Low Power).
    -   Verify: Button turns Green/Bold. Others gray out.
    -   Click "PŘETÍŽENÍ" (Overclock).
    -   Verify: Button turns Red/Bold.
    -   Click "NORMÁL".
    -   Verify: Button turns White/Bold.

4.  **Test Hyper Vis Switches:**
    -   Click "ČERNÁ SKŘÍŇKA".
    -   Verify: Button highlights (underline/bg).
    -   Click "ŽÁDNÝ".
    -   Verify: Highlight moves.

5.  **Test Persistence:**
    -   Reload the page.
    -   Go back to Controls.
    -   Verify: The previously selected modes are still highlighted (fetched from API).
