# IRIS System - Operator Manual

**Target Audience:** Game Masters / Tech Support
**Event:** Project IRIS LARP

---

## 1. System Credentials

These accounts are auto-generated on the first system run.

### Root Control
*   **Username:** `root`
*   **Password:** `master_control_666`
*   **Role:** Admin (Elite)
*   **Purpose:** Restarting system, changing global game constants.

### Game Masters (Admins)
*   `admin1` / `secure_admin_1`
*   `admin2` / `secure_admin_2`
*   `admin3` / `secure_admin_3`
*   `admin4` / `secure_admin_4`

### Agents (Hlinik Operators)
*   `agent1` / `agent_pass_1` (Terminal 1)
*   `agent2` / `agent_pass_2` (Terminal 2)
*   ...
*   `agent8` / `agent_pass_8` (Terminal 8)

### Users (Subjects)
*   `user1` / `subject_pass_1` (Session 1)
*   `user2` / `subject_pass_2` (Session 2)
*   ...
*   `user8` / `subject_pass_8` (Session 8)

---

## 2. Deployment Instructions

1.  **Start Server:**
    ```bash
    cd /path/to/IRIS_LARP
    source venv/bin/activate
    python run.py
    ```
2.  **Access:**
    *   Open Browser: `http://localhost:8000`
    *   Login with appropriate credentials.

---

## 3. Game Master Controls

### AI Configuration (Admin Only)
To enable Autopilot for Agents, you must configure the LLM provider.
1.  Click `[ AI CONFIG ]` in the dashboard header.
2.  **API Keys Tab**: Enter your OpenRouter (or other) API Key and click SAVE.
3.  **Hyper Tab**: Select `OPENROUTER` and update the Model/Prompt if needed. Default model is `google/gemini-2.0-flash-lite-preview-02-05:free`.

### Game State Controls
*   **Shift World**: Advances the global time shift. Agents/Users will see their session offset change.
*   **Chernobyl Meter**: Controls global instability.
    *   **0-20%**: Stable.
    *   **>80%**: Emergency Alarm, Red Tint, Heavy Glitching on ALL terminals.

---


## 3. Troubleshooting

*   **Database Lock:** If the system crashes, delete `data/iris.db` (Caution: data loss) and restart. It will re-seed.
*   **Login Failed:** Check caps lock. All passwords are case sensitive.
*   **Lag:** Refresh the browser page. The WebSocket should reconnect automatically.
