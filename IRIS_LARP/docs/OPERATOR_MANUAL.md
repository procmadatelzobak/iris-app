# IRIS System - Operator Manual

**Target Audience:** Game Masters / Tech Support  
**Event:** Project IRIS LARP  
**Version:** 2.0 (Phase 28)

---

## 1. System Credentials

These accounts are auto-generated from `data/default_scenario.json` on first run.

### Root Control
*   **Username:** `root`
*   **Password:** `master_control_666`
*   **Role:** Admin (Elite)
*   **Purpose:** System restart, factory reset, changing global game constants.

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

## 2. Installation

### First Run (Manual)
```bash
cd /path/to/IRIS_LARP
chmod +x install.sh run.sh
./install.sh
./run.sh
```

### Auto-Start (Systemd)
1. Copy and edit the service file:
   ```bash
   sudo cp iris.service /etc/systemd/system/
   sudo nano /etc/systemd/system/iris.service
   # Update: User, WorkingDirectory, ExecStart paths
   ```

2. Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable iris
   sudo systemctl start iris
   ```

3. Check status:
   ```bash
   sudo systemctl status iris
   journalctl -u iris -f  # Live logs
   ```

---

## 3. Web-Based System Control (ROOT Only)

### Access
Login as `root` -> Click `PANOPTICON` -> Use `EXECUTIVE PROTOCOLS` panel.

### Available Actions

| Button | Action |
|--------|--------|
| **SYSTEM RESET** | Wipes logs, tasks, resets user credits. Keeps database. |
| **RESTART SERVER** | Gracefully restarts the Python process. ~5 second downtime. |
| **FACTORY RESET** | **DELETES DATABASE**, restarts with fresh `default_scenario.json`. All data lost! |

### Customizing Default Scenario
Edit `data/default_scenario.json` to change:
- Number of admins/agents/users
- Password patterns
- Initial credits
- Economy defaults (treasury, tax rate)
- Power settings
- LLM configuration

---

## 4. Game Master Controls

### AI Configuration (Admin Only)
1. Click `[ AI CONFIG ]` in the dashboard header.
2. **API Keys Tab**: Enter your OpenRouter API Key and click SAVE.
3. **Hyper Tab**: Select model, update prompt.

### Game State Controls
*   **Shift World**: Advances global time shift.
*   **Temperature Meter**: Controls instability (0-350°, >350 = glitch mode).
*   **Power Bar**: Shows load vs capacity.

---

## 5. Dashboard Tabs (Admin)

1. **MONITOR**: Real-time grid of all User sessions.
2. **CONTROLS**: Shift, Power, Temperature, Visibility modes.
3. **ECONOMY**: Manage credits, fines, lockouts.
4. **TASKS**: Review and pay/reject submissions.

---

## 6. Troubleshooting

| Issue | Solution |
|-------|----------|
| Database Lock | Delete `data/iris.db` and restart. |
| Login Failed | Check caps lock. Passwords are case-sensitive. |
| Lag | Refresh browser. WebSocket auto-reconnects. |
| Server Won't Start | Check `server.log`, verify `venv` exists. |
| Factory Reset Stuck | Manually kill process, delete `data/iris.db`, restart. |

---

## 7. File Structure

```
IRIS_LARP/
├── app/              # Python application
├── data/
│   ├── default_scenario.json  # Default configuration
│   ├── iris.db                # SQLite database (auto-created)
│   └── admin_labels.json      # Custom labels
├── static/           # CSS, JS, assets
├── docs/             # Documentation
├── install.sh        # Installation script
├── run.sh            # Start script
├── run.py            # Python entry point
├── iris.service      # Systemd service template
└── requirements.txt  # Python dependencies
```

---

## 8. Security Notes

**Files NOT committed to git:**
- `data/*.db` - Database files
- `data/admin_labels.json` - Runtime config
- `.env` - API keys
- `server.log` - Server logs
- `venv/` - Virtual environment

**DO NOT** share `default_scenario.json` if it contains production passwords.
