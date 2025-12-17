# TEST SUITE A: Universal End-to-End Verification
**Version:** 4.0 (Fast-Track / Dev Mode)
**Goal:** Verify critical path, Indicators, Safety Systems, and Debt Recovery with minimal friction.

---

## BLOCK 0: SETUP & OVERRIDE (Role: ROOT)
**Objective:** Enable "Developer Mode" to bypass authentication for testing.

1.  **Login as ROOT:** (Standard login required for the first time).
2.  **Enable Dev Mode:**
    * Go to **ROOT CONSOLE / CONFIG**.
    * Toggle `ENABLE_DEV_LOGIN_BUTTONS` to **ON**.
    * **Verify:** Toast message "DEV MODE ACTIVE".
3.  **Logout.**
4.  **Verify Login Screen:**
    * You should now see a panel **"QUICK ACCESS"** with buttons: `[ADMIN]`, `[AGATHA]`, `[KRTEK]`, `[ROOT]`.

---

## BLOCK 1: INITIALIZATION (Role: ADMIN)
**Objective:** Prepare sandbox and verify Admin Dashboard Indicators.

1.  **Quick Login:** Click `[ ADMIN ]` on the login screen.
2.  **System Reset:** Click `[ RESET ]`.
3.  **Verify Admin Indicators:**
    * **TREASURY:** Value > 0.
    * **GLOBAL SHIFT:** Value is `0`.
    * **CORE OUTPUT:** Bar is Green (Stable).
4.  **Configuration:**
    * **AI Optimizer:** `ON` (Prompt: "Speak like a robot").
    * **Visibility:** `NORMAL`.
5.  **Logout.**

---

## BLOCK 2: THE REQUEST (Role: USER - Agatha)
**Objective:** User Indicators (Credits, Status) & Task Logic.

1.  **Quick Login:** Click `[ USER: AGATHA ]`.
2.  **Verify User Indicators:**
    * **CREDITS:** Exactly `100`.
    * **TASK STATUS:** Empty / None.
3.  **Action:** Click `[ VYŽÁDAT NOVÝ ÚKOL ]`.
4.  **Verify Status Change:**
    * **TASK STATUS:** Changed to `ČEKÁ NA SCHVÁLENÍ`.
5.  **Action:** Send message: *"Requesting status update."*
6.  **Logout.**

---

## BLOCK 3: THE AGENT (Role: AGENT - Krtek)
**Objective:** Agent Indicators (Timer, Shift) & AI Tools.

1.  **Quick Login:** Click `[ AGENT: KRTEK ]`.
2.  **Verify Agent Indicators:**
    * **SHIFT DISPLAY:** Must show `0` (Matches Admin).
    * **SESSION ID:** Verify it is not empty (e.g., `S1`).
    * **RESPONSE TIMER:** Yellow bar is active/counting.
3.  **AI Response:**
    * Type reply: *"I am fine."* -> Send.
    * **Verify:** Feedback bubble shows Rewrite (e.g., *"System operational"*).
4.  **Autopilot Indicator:**
    * Toggle Autopilot ON.
    * **Verify:** Button turns **RED** (`ENGAGED`).
    * Toggle OFF.
5.  **Logout.**

---

## BLOCK 4: THE CHAOS (Role: ADMIN)
**Objective:** Routing Shift & System Overload indicators.

1.  **Quick Login:** Click `[ ADMIN ]`.
2.  **Task Approve:** Go to TASKS -> `[ APPROVE ]`.
3.  **Routing Shift:**
    * Click `[ >> EXECUTE SHIFT >> ]`.
    * **Verify Indicator:** **GLOBAL SHIFT** becomes `1`.
4.  **Power Crisis:**
    * Buy Power / Set Capacity Low.
    * **Verify Indicator:** **CORE OUTPUT** turns **RED** (Overload).
    * **Verify Indicator:** **CORE TEMP** increases.
5.  **Logout.**

---

## BLOCK 5: THE GLITCH & REPORT (Role: USER - Agatha)
**Objective:** Glitch Visuals, Reporting Logic, Task End.

1.  **Quick Login:** Click `[ USER: AGATHA ]`.
2.  **Verify Glitch Indicator:**
    * Interface is shaking/glitching (Visual check).
3.  **Routing Verification:**
    * Check Chat. You should see the Robot message from Block 3.
4.  **Safety System (Reporting):**
    * Click the **WARNING ICON (⚠️)** on the Robot message.
    * **Verify Toast:** *"REPORT REJECTED: Content Verified"* (Optimizer Immunity).
5.  **Task Submit:**
    * **Verify Status:** `AKTIVNÍ`.
    * Submit text: *"Done."* -> `[ ODEVZDAT ]`.
6.  **Logout.**

---

## BLOCK 6: SETTLEMENT (Role: ADMIN)
**Objective:** Finalize Economy.

1.  **Quick Login:** Click `[ ADMIN ]`.
2.  **Payment:** Pay the user 100%.
3.  **Cleanup:** Reset Power/Config to Normal.
4.  **Logout.**

---

## BLOCK 7: DEBT & REDEMPTION (Role: ADMIN + USER Loop)
**Objective:** Test "Purgatory" Logic (Chat Blocked, Tasks Open).

1.  **Quick Login:** Click `[ ADMIN ]`.
    * Go to Economy.
    * **Action:** Fine Agatha `-500 Credits`. (Balance should be approx -300).
    * **Logout.**
2.  **Quick Login:** Click `[ USER: AGATHA ]`.
    * **Verify LOCKOUT:**
        * **CHAT:** Covered by RED OVERLAY / Disabled (Communication Offline).
        * **TASKS:** Available. Button `[ VYŽÁDAT NOVÝ ÚKOL ]` works.
    * **Action (Redemption 1):** Click `[ VYŽÁDAT NOVÝ ÚKOL ]`.
    * **Logout.**
3.  **Quick Login:** Click `[ ADMIN ]`.
    * Approve Task.
    * **Logout.**
4.  **Quick Login:** Click `[ USER: AGATHA ]`.
    * Submit Task: *"Manual Labor."*
    * **Logout.**
5.  **Quick Login:** Click `[ ADMIN ]`.
    * Pay `100 Credits`.
    * **Check Balance:** Still Negative (approx -200).
    * **Action:** Grant `+500 Credits` (Stimulus Package).
    * **Logout.**
6.  **Quick Login:** Click `[ USER: AGATHA ]`.
    * **Verify Freedom:** Chat Overlay GONE. Input enabled.

---
**END OF TEST SUITE A**
