# IRIS LARP - Technical Specification
**Version:** Phase 25.0  
**Date:** 2025-12-14  
**Status:** Living Document

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [User Roles & Permissions](#user-roles--permissions)
4. [Core Features](#core-features)
5. [API Reference](#api-reference)
6. [Database Schema](#database-schema)
7. [WebSocket Protocol](#websocket-protocol)
8. [Security](#security)

---

## 1. System Overview

IRIS LARP is a **real-time multiplayer role-playing game system** designed for live-action role-playing (LARP) events. The platform facilitates communication between **Users** (subjects), **Agents** (operators), and **Admins** (game masters) through a sophisticated terminal interface with AI-assisted features.

### Key Characteristics:
- **Real-time Communication**: WebSocket-based instant messaging
- **AI Integration**: LLM-powered message optimization and autopilot
- **Economic System**: Credit-based economy with task rewards
- **Dynamic Routing**: Session-based agent assignment with shift mechanics
- **Visual Themes**: Role-based UI theming (Low/Mid/High/Party)
- **Admin Controls**: Comprehensive game master dashboard

---

## 2. Architecture

### 2.1 Technology Stack

**Backend:**
- **Framework**: FastAPI (Python 3.10+)
- **Database**: SQLite + SQLAlchemy ORM
- **WebSockets**: Native FastAPI WebSocket support
- **Authentication**: JWT tokens + HTTP-only cookies
- **AI/LLM**: OpenRouter API, OpenAI API

**Frontend:**
- **Templates**: Jinja2
- **Styling**: Tailwind CSS + Custom CSS
- **JavaScript**: Vanilla ES6+ (no frameworks)
- **WebSocket Client**: Custom `SocketClient` class
- **Sound**: Custom `SoundEngine` for audio feedback

### 2.2 Project Structure

```
IRIS_LARP/
├── app/
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Environment configuration
│   ├── database.py             # SQLAlchemy models
│   ├── dependencies.py         # Auth & DB dependencies
│   ├── seed.py                 # Database seeding
│   ├── logic/
│   │   ├── gamestate.py        # Global game state singleton
│   │   ├── routing.py          # WebSocket routing logic
│   │   ├── economy.py          # Credit & task economy
│   │   └── llm_core.py         # LLM integration
│   ├── routers/
│   │   ├── auth.py             # Login, logout, terminal routing
│   │   ├── sockets.py          # WebSocket endpoint
│   │   └── admin_api.py        # Admin REST API
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── user_terminal.html
│       ├── agent_terminal.html
│       └── admin/
│           ├── dashboard.html  # Standard admin dashboard
│           └── root_dashboard.html  # ROOT console
├── static/
│   ├── css/
│   │   ├── terminal.css        # Base terminal styling
│   │   ├── admin_chernobyl.css # Admin theme
│   │   └── user_themes.css     # User theme system
│   └── js/
│       ├── socket_client.js    # WebSocket client
│       ├── sound_engine.js     # Audio feedback
│       └── admin_ui.js         # Admin dashboard logic
├── data/
│   └── iris.db                 # SQLite database
├── tests/                      # Test suite
└── docs/                       # Documentation
```

### 2.3 Component Interaction

```
[Browser Client] <--WebSocket--> [FastAPI Server]
       |                              |
       |                              ├─> [GameState Singleton]
       |                              ├─> [Routing Logic]
       |                              ├─> [Economy System]
       |                              ├─> [LLM Service]
       |                              └─> [SQLite DB]
```

---

## 3. User Roles & Permissions

### 3.1 Role Hierarchy

| Role    | Username Pattern | Default Count | Access Level |
|---------|------------------|---------------|--------------|
| **ROOT**    | `root`       | 1             | Elite Admin  |
| **ADMIN**   | `admin1-4`   | 4             | Game Master  |
| **AGENT**   | `agent1-8`   | 8             | Operator     |
| **USER**    | `user1-8`    | 8             | Subject      |

### 3.2 Permission Matrix

| Feature                   | ROOT | ADMIN | AGENT | USER |
|---------------------------|------|-------|-------|------|
| View Dashboard            | ✅   | ✅    | ❌    | ❌   |
| Manage Economy            | ✅   | ✅    | ❌    | ❌   |
| Approve Tasks             | ✅   | ✅    | ❌    | ❌   |
| Execute Shift             | ✅   | ✅    | ❌    | ❌   |
| Configure LLM             | ✅   | ❌    | ❌    | ❌   |
| System Reset              | ✅   | ❌    | ❌    | ❌   |
| Test Mode Toggle          | ✅   | ❌    | ❌    | ❌   |
| Send Messages (Chat)      | ❌   | ❌    | ✅    | ✅   |
| Use AI Optimizer          | ❌   | ❌    | ✅    | ❌   |
| Toggle Autopilot          | ❌   | ❌    | ✅    | ❌   |
| Request Tasks             | ❌   | ❌    | ❌    | ✅   |
| Report Messages           | ❌   | ❌    | ❌    | ✅   |

---

## 4. Core Features

### 4.1 Communication System

**Session-Based Chat:**
- 8 isolated chat sessions matching 8 users
- Agents are **dynamically routed** to sessions based on **Global Shift Offset**
- Formula: `Agent Session = (Agent_ID - 1 + Shift) % 8 + 1`

**Message Flow:**
1. User sends message → Saved to ChatLog → Broadcast to assigned Agent
2. Agent sends message → (Optional: AI Optimizer) → Saved → Broadcast to User

**Purgatory Mode:**
- Users with negative credits enter "Purgatory"
- **Chat Blocked**: Cannot send/receive messages
- **Tasks Allowed**: Can still request and submit tasks to recover credit

### 4.2 AI Features

**1. Message Optimizer (Agents)**
- **Purpose**: Rewrite agent messages in a specific tone/style
- **Model**: Configurable (default: GPT-4o-mini)
- **Flow**:
  1. Agent types message → Send
  2. Backend processes via LLM with custom prompt
  3. **Preview** sent back to Agent
  4. Agent **Confirms** or **Rejects**
  5. On confirm: Optimized version saved & broadcast
- **Immunity**: Optimized messages cannot be Reported

**2. Autopilot (Agents)**
- **Purpose**: AI auto-responds to users
- **Model**: Configurable (default: Gemini 2.0 Flash Lite)
- **Behavior**:
  - Maintains conversation history per session
  - Generates contextual responses
  - Saves responses with Agent's ID
- **Control**: Toggle ON/OFF per agent

### 4.3 Economy System

**Credits:**
- Users start with **100 credits**
- Admins can grant bonuses or fines
- **Lockout Threshold**: Credits < 0 triggers Purgatory

**Tasks:**
- **States**: `PENDING_APPROVAL` → `ACTIVE` → `COMPLETED`/`REJECTED`
- **Flow**:
  1. User requests task → Admin assigns description & reward
  2. Admin approves → Task becomes ACTIVE
  3. User submits completion text
  4. Admin pays reward → Credits updated

**Tax System:**
- Configurable tax rate (default: 20%)
- Applied to task rewards
- Funds the "Treasury" (admin-controlled)

### 4.4 Routing & Shift System

**Global Shift Offset:**
- Integer value (0-7)
- Controls which Agent sees which User session
- Changed via "EXECUTE SHIFT" button (increments by 1, wraps at 8)

**Example Routing:**
| Shift | Agent1 sees | Agent2 sees | ... | Agent8 sees |
|-------|-------------|-------------|-----|-------------|
| 0     | User1       | User2       | ... | User8       |
| 1     | User2       | User3       | ... | User1       |
| 7     | User8       | User1       | ... | User7       |

**Visibility Modes:**
- **NORMAL**: Agents see full chat history
- **BLACKBOX**: Agents see NO history (blind start)
- **FORENSIC**: Enhanced view (implementation pending)

### 4.5 Theme System

Users are assigned visual themes based on `status_level`:

| Status | Theme   | Colors        | Special Effects      |
|--------|---------|---------------|----------------------|
| `low`  | Basic   | Green/Black   | -                    |
| `mid`  | Nature  | Green/Earth   | -                    |
| `high` | Luxury  | Gold/Purple   | -                    |
| `party`| Chaos   | Pink/Rainbow  | Bubble animations    |

Themes are dynamically switched via WebSocket `theme_update` message.

### 4.6 Test Mode (Developer)

**Purpose**: Rapid testing during development  
**Activation**: ROOT dashboard → CONFIG tab → Toggle "Quick Login Buttons"

**Effect:**
- Login screen displays buttons for all seeded users
- Click button → Auto-fills correct password → Submits
- No manual typing required

**Security**: Should be **DISABLED** in production

---

## 5. API Reference

### 5.1 Authentication

#### POST `/auth/login`
**Body**: `username`, `password` (form-data)  
**Returns**: `{ "access_token", "token_type", "role" }`  
**Cookie**: Sets `access_token` (HttpOnly=false, Path=/)

#### GET `/auth/logout`
**Effect**: Deletes `access_token` cookie, redirects to login

#### GET `/auth/terminal`
**Auth**: Required (cookie)  
**Returns**: HTML (role-specific terminal)

---

### 5.2 Admin API (Prefix: `/api/admin`)

#### Economy

**POST `/economy/bonus`**
```json
{
  "user_id": 1,
  "amount": 50,
  "reason": "Good work"
}
```

**POST `/economy/set_status`**
```json
{
  "user_id": 1,
  "status": "party"
}
```

#### ROOT (Elite Admin Only)

**GET `/root/state`**
```json
{
  "tax_rate": 0.2,
  "power_cap": 100,
  "treasury": 500,
  "costs": { ... }
}
```

**POST `/root/ai_config`**
```json
{
  "optimizer_prompt": "Speak like a robot",
  "autopilot_model": "google/gemini-2.0-flash-lite-preview-02-05:free"
}
```

**POST `/root/reset`**
- Wipes logs, resets user credits, clears tasks
- Resets gamestate to defaults

---

### 5.3 WebSocket Protocol

#### Connection
**URL**: `ws://localhost:8000/ws/connect?token=<JWT>`

#### Message Types (Client → Server)

**User:**
```json
{ "content": "Hello agent" }
{ "type": "task_request" }
{ "type": "report_message", "id": 123 }
{ "type": "typing_sync", "content": "partial text..." }
```

**Agent:**
```json
{ "content": "Hello user" }
{ "type": "autopilot_toggle", "status": true }
{ "type": "typing_sync", "content": "..." }
{ "confirm_opt": true, "content": "optimized text" }
```

**Admin:**
```json
{ "type": "shift_command" }
{ "type": "temperature_command", "value": 150 }
{ "type": "admin_broadcast", "content": "System alert" }
{ "type": "test_mode_toggle", "enabled": true }
```

#### Message Types (Server → Client)

```json
{ "type": "gamestate_update", "shift": 1, "temperature": 120, ... }
{ "type": "theme_update", "theme": "party" }
{ "type": "lock_update", "locked": true }
{ "type": "task_update", "status": "active", "description": "...", "reward": 50 }
{ "type": "optimizer_preview", "original": "...", "rewritten": "..." }
{ "type": "report_denied", "reason": "SYSTEM_VERIFIED" }
```

---

## 6. Database Schema

### Users
| Column         | Type    | Description                    |
|----------------|---------|--------------------------------|
| id             | INTEGER | Primary key                    |
| username       | VARCHAR | Unique                         |
| password_hash  | VARCHAR | Bcrypt hash                    |
| role           | ENUM    | USER/AGENT/ADMIN               |
| credits        | INTEGER | Current balance                |
| is_locked      | BOOLEAN | Purgatory status               |
| status_level   | VARCHAR | Theme: low/mid/high/party      |

### ChatLog
| Column      | Type     | Description                  |
|-------------|----------|------------------------------|
| id          | INTEGER  | Primary key                  |
| session_id  | INTEGER  | 1-8                          |
| sender_id   | INTEGER  | FK → Users.id                |
| content     | TEXT     | Message text                 |
| timestamp   | DATETIME | Auto                         |
| is_optimized| BOOLEAN  | Optimizer used?              |
| was_reported| BOOLEAN  | User reported this?          |

### Tasks
| Column       | Type    | Description                      |
|--------------|---------|----------------------------------|
| id           | INTEGER | Primary key                      |
| user_id      | INTEGER | FK → Users.id                    |
| prompt_desc  | TEXT    | Task description                 |
| reward_offered| INTEGER| Credits to pay                   |
| status       | ENUM    | PENDING/ACTIVE/COMPLETED/REJECTED|
| created_at   | DATETIME| Auto                             |

### SystemLog
| Column     | Type     | Description                     |
|------------|----------|---------------------------------|
| id         | INTEGER  | Primary key                     |
| event_type | VARCHAR  | ACTION/ROOT/REPORT/TASK         |
| message    | TEXT     | Human-readable log              |
| data       | TEXT     | JSON metadata                   |
| timestamp  | DATETIME | Auto                            |

---

## 7. WebSocket Protocol

See section 5.3 above for detailed message schemas.

**Connection Lifecycle:**
1. Client connects with JWT token
2. Server validates & retrieves User
3. Server sends initial state (history, user status)
4. Bidirectional message exchange
5. On disconnect: Server cleans up routing tables

---

## 8. Security

### 8.1 Authentication
- **JWT Tokens**: HS256 algorithm
- **Cookie-based**: HttpOnly for XSS protection
- **Expiration**: 1440 minutes (24 hours)

### 8.2 Authorization
- Role checks in `dependencies.py` (`get_current_admin`)
- WebSocket: Token validation on connect
- API: Depends injection ensures auth

### 8.3 Best Practices
- **Passwords**: Bcrypt hashing (cost=12)
- **SQL**: SQLAlchemy ORM prevents injection
- **Secrets**: Environment variables (`.env`)
- **Input Validation**: Pydantic models

### 8.4 Known Limitations
- ⚠️ **Test Mode**: Exposes all users (DEV only)
- ⚠️ **No HTTPS**: Local deployment assumes trusted network
- ⚠️ **Single-Tenant**: No multi-organization support

---

**Document Version**: Phase 25.0  
**Last Updated**: 2025-12-14  
**Maintainer**: Development Team
