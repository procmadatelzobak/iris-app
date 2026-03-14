# Project IRIS: System Architecture & Design Document

**Version:** 1.0 **Target Audience:** Development Team / AI Coding Agent **Language:** English (Technical Specs)

## 1. Executive Summary

The IRIS System is a closed-network web application designed to facilitate a high-fidelity LARP (Live Action Role-Playing) simulation. It simulates a "Wizard of Oz" AI environment where human Agents pretend to be an AI (HLINIK) interacting with Users. The system features real-time chat, complex economic modeling, administrative oversight ("God Mode"), and LLM integration for "Autopilot" functionality.

**Core Design Philosophy:**

-   **Stability:** The system must not crash during the 48-hour event.
    
-   **Real-time:** Sub-millisecond latency for chat and UI updates via WebSockets.
    
-   **Portability:** Zero-dependency deployment (GitHub -> Run). No external database servers (Postgres/Redis) required.
    
-   **Security through Obscurity:** The client is "dumb"; all logic (economy, routing, visibility) is strictly server-side.
    

## 2. Technical Architecture

### 2.1. Tech Stack

-   **Language:** Python 3.10+
    
-   **Backend Framework:** FastAPI (Asynchronous, high-performance, native WebSockets).
    
-   **Database:** SQLite (with WAL mode enabled for concurrency). Used for persistent storage of logs, users, and economy.
    
-   **In-Memory State:** Python `dataclasses` for real-time state (Sessions, Shift offsets, Hyper status) to ensure speed.
    
-   **Frontend:** Plain HTML5 / CSS3 (TailwindCSS via local script) / Vanilla JavaScript. No build steps (React/Vue/Node.js) to ensure easy deployment and modification.
    
-   **Communication:** WebSockets (JSON payloads) for all game interactions; REST API for initialization and media assets.
    
-   **LLM Integration:** OpenAI API (or compatible local LLM endpoint) via asynchronous HTTP client (`httpx`).
    

### 2.2. Network Topology & Hardware

-   **Server:** Central Python process running on a local machine/server.
    
-   **Clients:** Browser-based interfaces running on local tablets/laptops.
    
    -   `User Terminal`: The interface for game players (Subject).
        
    -   `Agent Terminal`: The interface for human operators (HLINIK).
        
    -   `Admin Dashboard`: The control center (4 distinct screens/views).
        
-   **Authentication:** "Terminal-based" Login. Users/Agents log in with credentials. The system allows multiple active tabs per user (Mirroring), enabling admins to "spy" or replace hardware seamlessly.
    

## 3. Core Logic & Mechanics

### 3.1. The Session Concept (The Routing Core)

The system revolves around fixed **Logical Sessions** ($S_1$ to $S_8$). A Session is the container for a conversation.

-   **Routing Logic:**
    
    -   **User Binding:** $User_X$ is permanently bound to $Session_X$.
        
    -   **Agent Binding:** $Agent_Y$ connects to a Session based on the current **Global Shift Offset**.
        
    -   **Formula:** `ConnectedSessionID = (AgentTerminalID + GlobalShiftOffset) % TotalSessions`
        
-   **The Restart (Shift +1):**
    
    -   When Admins trigger a "Restart", the `GlobalShiftOffset` increments by 1.
        
    -   The WebSocket manager immediately re-routes Agent connections to their new Session.
        
    -   _Effect:_ The Agent sitting at Terminal 1 suddenly sees the chat history (or lack thereof) of User 2.
        

### 3.2. The "Hyper" Mode (AI Autopilot)

-   **Concept:** Agents can "pause" their manual input to take a break. An LLM takes over.
    
-   **Visibility Logic (The 4-Way Switch):** Admins control what Agents see when they return from a break. This is controlled by a global variable `HyperVisibilityMode`:
    
    1.  **Transparent:** Agent sees HYPER generation live and history is preserved.
        
    2.  **Ephemeral:** Agent sees generation live, but history is DELETED upon unlocking the terminal.
        
    3.  **Blackbox:** Agent sees a blank screen while locked. History is HIDDEN/DELETED upon unlock.
        
    4.  **Forensic:** Agent sees a blank screen while locked. History APPEARS upon unlock (Paranoia mode).
        

### 3.3. Economy & Status

-   **Credits:** The currency.
    
    -   Gained via: Completing Tasks, Admin Bonuses, Reporting Anomalies (correctly).
        
    -   Lost via: Chatting (Efficiency Fine), Admin Penalties.
        
-   **Lockout State:**
    
    -   Trigger: `Credits <= 0`.
        
    -   Effect: Terminal locks. User cannot chat or request tasks. Displays "Manual Calibration Required".
        
    -   Resolution: Admin manually restores access via Dashboard.
        
-   **Social Status:**
    
    -   Levels: Low (Plevel), Mid (Standard), High (Elite).
        
    -   Effect: Determines the CSS theme of the User Terminal and the complexity/reward of generated tasks.
        

### 3.4. The Chernobyl Meter (Critical Indicator A)

-   **Visual:** An infinite progress bar on the Admin Dashboard.
    
-   **Logic:**
    
    -   Value increases with every User Report.
        
    -   Value decays over time (configurable decay rate).
        
    -   Can "overflow" (change colors) but never stops.
        
-   **Modifiers:** Admins can toggle "Low Power Mode" (High Latency, High Decay) or "Overclock" (Low Latency, No Decay).
    

## 4. Database Schema (SQLite)

-   **Users:**
    
    -   `id` (int, pk)
        
    -   `username` (str)
        
    -   `password_hash` (str)
        
    -   `role` (enum: 'user', 'agent', 'admin')
        
    -   `credits` (int)
        
    -   `status_level` (enum: 'low', 'mid', 'high')
        
    -   `is_locked` (bool)
        
-   **ChatLog:**
    
    -   `id` (int, pk)
        
    -   `session_id` (int)
        
    -   `sender_id` (fk -> Users)
        
    -   `content` (text)
        
    -   `timestamp` (datetime)
        
    -   `is_hyper` (bool) - Was this generated by AI?
        
    -   `is_hidden_for_agent` (bool) - For "Ephemeral/Blackbox" modes.
        
    -   `was_reported` (bool)
        
-   **Tasks:**
    
    -   `id` (int, pk)
        
    -   `user_id` (fk -> Users)
        
    -   `prompt_desc` (text)
        
    -   `reward_offered` (int)
        
    -   `status` (enum: 'pending_approval', 'active', 'submitted', 'completed')
        
    -   `submission_content` (text)
        
    -   `final_rating` (int percentage)
        
-   **SystemConfig:**
    
    -   `key` (str, pk) - e.g., 'global_shift_offset', 'hyper_visibility', 'chernobyl_value'
        
    -   `value` (str/json)
        

## 5. UI/UX Specifications

### 5.1. User Terminal

-   **Layout:** 3-Column (Stats & Status | Task Panel | Chat).
    
-   **Interactive Elements:**
    
    -   Chat bubbles have a discreet "Report" icon.
        
    -   "Request Task" button triggers async flow.
        
-   **Visual Feedback:**
    
    -   Credit updates animate (+Green / -Red).
        
    -   Theme changes dynamically based on Status Level.
        

### 5.2. Admin Dashboard (The Bridge)

-   **Navigation:** Top bar to switch views.
    
-   **View A: Monitoring:** 8x Chat Log components. Real-time updates.
    
-   **View B: Controls:**
    
    -   "Restart System" (Covered Toggle + Button).
        
    -   "Hyper Visibility" (Rotary Switch / 4 Radio Buttons).
        
    -   "Chernobyl Meter" (Canvas/CSS driven infinite bar).
        
-   **View C: Economy:**
    
    -   Table of Users.
        
    -   Actions: [Fine], [Bonus], [Lock/Unlock].
        
    -   Overlay Message input ("Send Notification").
        
-   **View D: Task Master:**
    
    -   Inbox: Pending Task Requests.
        
    -   Action: "Generate with AI" -> Edit -> Approve.
        
    -   Inbox: Submitted Tasks.
        
    -   Action: Slider (0-200%) -> Pay.
        

## 6. Directory Structure

```
IRIS_LARP/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point, WebSocket manager
│   ├── config.py            # Settings (LLM keys, constants)
│   ├── database.py          # SQLite setup & models
│   ├── dependencies.py      # Auth & DB injection
│   ├── logic/
│   │   ├── economy.py       # Credit/Status/Lockout logic
│   │   ├── routing.py       # Session & Shift logic
│   │   ├── llm_tools.py     # OpenAI wrappers (Hyper & Tasks)
│   │   └── gamestate.py     # In-memory Global State (Chernobyl meter etc.)
│   ├── routers/
│   │   ├── auth.py          # HTTP Login
│   │   ├── sockets.py       # Main WebSocket Endpoint
│   │   └── admin_api.py     # REST endpoints for Dashboards
│   └── templates/           # Jinja2 Templates
│       ├── base.html
│       ├── user_terminal.html
│       ├── agent_terminal.html
│       ├── admin_layout.html
│       └── admin/
│           ├── monitor.html
│           ├── controls.html
│           ├── economy.html
│           └── tasks.html
├── static/
│   ├── css/
│   │   ├── tailwind.min.css # Local copy
│   │   └── terminal.css     # Custom themes
│   ├── js/
│   │   ├── socket_client.js # Shared WS logic
│   │   └── admin_ui.js
│   └── sounds/              # alerts.mp3, glitch.mp3
├── data/
│   └── iris.db              # Ignored in git
├── tests/
│   ├── test_routing.py
│   └── test_economy.py
├── requirements.txt
└── run.py                   # Launcher

```

## 7. Requirements (requirements.txt)

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
websockets>=12.0
sqlalchemy>=2.0.25
jinja2>=3.1.3
openai>=1.10.0
python-dotenv>=1.0.0
aiofiles>=23.2.1
httpx>=0.26.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.7

```

## 8. Development Roadmap

1.  **Phase 1: Skeleton & Auth**
    
    -   Set up FastAPI, SQLite, and User/Agent Login.
        
    -   Implement WebSocket connection handling with basic Echo.
        
2.  **Phase 2: The Routing Core**
    
    -   Implement `Session` objects.
        
    -   Implement `GlobalShiftOffset`.
        
    -   Test: Two Agents swapping Sessions instantly.
        
3.  **Phase 3: Client Terminals**
    
    -   Build HTML/CSS for User and Agent.
        
    -   Implement Chat UI.
        
    -   Implement "Hyper" locking mechanism (UI only).
        
4.  **Phase 4: Admin Controls & Logic**
    
    -   Build Admin Dashboard B (Controls).
        
    -   Implement `HyperVisibility` filters in the WebSocket stream.
        
    -   Implement `ChernobylMeter` background task.
        
5.  **Phase 5: Economy & LLM**
    
    -   Connect OpenAI API.
        
    -   Implement Task Generation & Submission flow.
        
    -   Implement Credit deduction/addition and Lockout logic.
        
6.  **Phase 6: Polish**
    
    -   Add Sounds and Glitch effects.
        
    -   Stress testing.
        

## 9. Testing Strategy

-   **Unit Tests:** Focus on the `routing.py` logic. Ensure mathematical mapping of `(Agent + Shift) -> Session` is flawless.
    
-   **Integration Tests:** Verify that a "Restart" command from Admin correctly broadcasts a "Reload/Reconnect" signal to all Agent sockets.
    
-   **Load Test:** Use a script to spawn 20 concurrent WebSocket clients sending 5 messages/sec to ensure the server handles the throughput without lag.
