# IRIS Systém - Architektura a Technický Popis

**Verze:** 2.0  
**Jazyk:** Český  
**Pro:** Systémový architekt / Vývojář

---

## Obsah

1. [Přehled systému](#1-přehled-systému)
2. [Architektura](#2-architektura)
3. [Role a oprávnění](#3-role-a-oprávnění)
4. [Komunikační protokol (WebSocket)](#4-komunikační-protokol-websocket)
5. [Herní logika](#5-herní-logika)
6. [Vizuální témata (Status Level)](#6-vizuální-témata-status-level)
7. [Synchronizace mezi zařízeními](#7-synchronizace-mezi-zařízeními)
8. [AI Funkcionalita](#8-ai-funkcionalita)
9. [Databázové schéma](#9-databázové-schéma)
10. [API Referenční příručka](#10-api-referenční-příručka)

---

## 1. Přehled systému

IRIS je webová aplikace pro LARP hru, kde hráči komunikují přes terminály. Systém simuluje dystopickou korporátní AI.

### Klíčové funkce
- Reálný čas komunikace přes WebSocket
- Systém úkolů a ekonomiky (kredity)
- AI optimalizace zpráv
- Vizuální efekty (glitch, témata)
- Administrátorský dashboard

### Technologie
| Komponenta | Technologie |
|------------|-------------|
| Backend | Python 3.10+, FastAPI |
| Frontend | HTML, Tailwind CSS, Vanilla JS |
| Databáze | SQLite (SQLAlchemy ORM) |
| Realtime | WebSockets |
| AI | OpenRouter / OpenAI API |

---

## 2. Architektura

```
┌─────────────────────────────────────────────────────────────┐
│                       KLIENT (Prohlížeč)                    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │  User   │  │  Agent  │  │  Admin  │  │  ROOT   │        │
│  │Terminal │  │Terminal │  │Dashboard│  │ Console │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │              │
│       └────────────┴────────────┴────────────┘              │
│                           │                                  │
│                    WebSocket + HTTP                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                       SERVER                                 │
│  ┌────────────────────────┴────────────────────────────┐    │
│  │                    FastAPI                           │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │    │
│  │  │  auth.py │  │sockets.py│  │admin_api │          │    │
│  │  │  (Login) │  │   (WS)   │  │  (REST)  │          │    │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘          │    │
│  │       │             │             │                 │    │
│  │       └─────────────┼─────────────┘                 │    │
│  │                     │                               │    │
│  │  ┌──────────────────┴────────────────────────┐     │    │
│  │  │              LOGIC LAYER                   │     │    │
│  │  │  ┌────────────┐ ┌──────────┐ ┌──────────┐ │     │    │
│  │  │  │ gamestate  │ │ routing  │ │ economy  │ │     │    │
│  │  │  │ (Singleton)│ │ (WS Mgr) │ │ (Credits)│ │     │    │
│  │  │  └────────────┘ └──────────┘ └──────────┘ │     │    │
│  │  │  ┌────────────┐ ┌──────────┐              │     │    │
│  │  │  │ llm_core   │ │llm_tools │              │     │    │
│  │  │  │ (AI Calls) │ │(Optimize)│              │     │    │
│  │  │  └────────────┘ └──────────┘              │     │    │
│  │  └───────────────────────────────────────────┘     │    │
│  └─────────────────────────────────────────────────────┘    │
│                            │                                 │
│  ┌─────────────────────────┴───────────────────────────┐    │
│  │                   SQLite DB                          │    │
│  │  Users, Tasks, ChatLogs, SystemLogs                  │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Role a oprávnění

### Role Hierarchy

| Role | Úroveň | Popis |
|------|--------|-------|
| **ROOT** | 4 | Gamemaster, plná kontrola |
| **ADMIN** | 3 | Správce, ovládá hru |
| **AGENT** | 2 | Operátor, odpovídá uživatelům |
| **USER** | 1 | Hráč, komunikuje s agentem |

### Přiřazení Session (Shift logika)

Každý USER a AGENT je přiřazen k Session (1-8) podle vzorce:

```
session_id = ((user_slot - 1) + global_shift_offset) % TOTAL_SESSIONS + 1
```

- `user_slot`: Číslo uživatele (1-8)
- `global_shift_offset`: Aktuální hodnota posunu (0-7)
- Změna shiftu způsobí přepárování User ↔ Agent

---

## 4. Komunikační protokol (WebSocket)

### Připojení
```
ws://<server>:8000/ws/connect
Headers: Authorization: Bearer <JWT>
```

### Typy zpráv (Client → Server)

| Type | Popis | Payload |
|------|-------|---------|
| `chat_message` | Odeslání zprávy | `{ content: string }` |
| `typing_sync` | Synchronizace psaní | `{ content: string }` |
| `task_request` | Žádost o úkol | `{}` |
| `task_submit` | Odevzdání úkolu | `{ task_id, answer }` |
| `report_message` | Nahlášení zprávy | `{ id: number }` |
| `autopilot_toggle` | Zapnutí autopilota | `{ enabled: boolean }` |
| `admin_broadcast` | Globální zpráva | `{ content: string }` |

### Typy zpráv (Server → Client)

| Type | Popis | Payload |
|------|-------|---------|
| `gamestate_update` | Aktualizace stavu | `{ temperature, shift, is_overloaded, ... }` |
| `user_status` | Stav uživatele | `{ credits, is_locked, shift }` |
| `task_update` | Aktualizace úkolu | `{ id, status, description }` |
| `optimizer_feedback` | AI přepis | `{ original, rewritten }` |
| `optimizing_start` | Začátek AI přepisu | `{}` |
| `server_restart` | Restart serveru | `{ message }` |
| `factory_reset` | Factory reset | `{ message }` |

---

## 5. Herní logika

### GameState (Singleton)

Centrální objekt držící herní stav:

| Atribut | Typ | Popis |
|---------|-----|-------|
| `global_shift_offset` | int | Aktuální shift (0-7) |
| `temperature` | float | Teplota systému (20-1000) |
| `power_capacity` | int | Max MW |
| `power_load` | int | Aktuální zatížení |
| `is_overloaded` | bool | Přetížení |
| `treasury_balance` | int | Pokladna |
| `tax_rate` | float | Daň z úkolů |
| `optimizer_active` | bool | AI přepisování |
| `test_mode` | bool | Testovací režim |

### Power Calculation

```python
load = COST_BASE                           # 10
load += COST_PER_USER * active_users       # 5 × users
load += COST_PER_AUTOPILOT * autopilots    # 10 × autopilots
if low_latency: load += COST_LOW_LATENCY   # +30
if optimizer: load += COST_OPTIMIZER       # +15
```

### Overload Condition

```python
is_overloaded = (power_load > power_capacity) or (temperature > TEMP_THRESHOLD)
```

---

## 6. Vizuální témata (Status Level)

Každý uživatel má `status_level`, který určuje vizuální téma terminálu.

### Dostupné úrovně

| Level | CSS Class | Popis | Barvy |
|-------|-----------|-------|-------|
| `low` | `theme-low` | Industriální, tmavé | Šedá, černá |
| `mid` | `theme-mid` | Přírodní, organické | Zelená, mátová |
| `high` | `theme-high` | Luxusní, elegantní | Zlatá, černá |
| `party` | `theme-party` | Party, zábavné | Růžová, bubliny |

### Aplikace tématu

V `user_terminal.html`:
```javascript
document.body.className = "theme-{{ user.status_level }}";
```

### CSS proměnné

Každé téma definuje:
- `--bg-color` - Barva pozadí
- `--text-color` - Barva textu
- `--accent-color` - Akcentová barva
- `--border-color` - Barva rámečků
- `--font-main` - Font
- `--radius` - Zaoblení rohů
- `--shadow` - Stíny

### Změna tématu za běhu

Správce může změnit téma uživatele přes WebSocket:
```json
{ "type": "theme_update", "theme": "party" }
```

---

## 7. Synchronizace mezi zařízeními

### Agent Synchronizace (Typing Sync)

Když Agent píše na jednom zařízení, text se synchronizuje na všechna ostatní:

```
┌──────────────┐    typing_sync    ┌──────────────┐
│ Agent Tab 1  │ ───────────────► │   Server     │
│ (Laptop)     │                  │ (sockets.py) │
└──────────────┘                  └──────┬───────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
             ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
             │ Agent Tab 1  │     │ Agent Tab 2  │     │ Agent Tab 3  │
             │ (Laptop)     │     │ (Tablet)     │     │ (Phone)      │
             └──────────────┘     └──────────────┘     └──────────────┘
```

**Implementace (sockets.py):**
```python
if cmd_type == "typing_sync":
    for conn in agent_connections[user.id]:
        if conn != websocket:  # Neposlat zpět odesílateli
            await conn.send_text(...)
```

### Admin View Sync

Všichni správci vidí stejnou záložku dashboardu:
```python
elif cmd_type == "admin_view_sync":
    await routing_logic.broadcast_to_admins(...)
```

### User Chat Sync

Uživatel může mít otevřeno více oken:
```python
if user.id in routing_logic.user_connections:
    for conn in routing_logic.user_connections[user.id]:
        if conn != websocket:
            await conn.send_text(...)
```

---

## 8. AI Funkcionalita

### Optimizer (Přepisování zpráv)

1. Agent pošle zprávu
2. Server zjistí, že `optimizer_active == True`
3. Server pošle `optimizing_start` Agentovi
4. Server zavolá LLM API s promptem
5. Server pošle `optimizer_preview` s původním a přepsaným textem
6. Agent potvrdí nebo odmítne
7. Finální zpráva je odeslána Uživateli s `is_optimized: true`

### Autopilot

1. Agent zapne autopilot (`autopilot_toggle`)
2. Příchozí zpráva od Uživatele
3. Server automaticky generuje odpověď pomocí LLM
4. Odpověď je odeslána jako zpráva od Agenta

### LLM Providers

| Provider | Config Key | Model Example |
|----------|------------|---------------|
| OpenAI | `OPENAI_API_KEY` | `gpt-4o` |
| OpenRouter | `OPENROUTER_API_KEY` | `google/gemini-2.0-flash-lite-preview-02-05:free` |

---

## 9. Databázové schéma

### User
| Sloupec | Typ | Popis |
|---------|-----|-------|
| id | INTEGER | PK |
| username | VARCHAR | Unikátní |
| password_hash | VARCHAR | Bcrypt hash |
| role | ENUM | USER/AGENT/ADMIN |
| credits | INTEGER | Default 100 |
| is_locked | BOOLEAN | Purgatory |
| status_level | ENUM | LOW/MID/HIGH/PARTY |

### Task
| Sloupec | Typ | Popis |
|---------|-----|-------|
| id | INTEGER | PK |
| user_id | FK | -> User |
| prompt_desc | TEXT | Popis úkolu |
| answer | TEXT | Odevzdaná odpověď |
| status | ENUM | PENDING/ACTIVE/SUBMITTED/PAID |
| reward_offered | INTEGER | Odměna |

### ChatLog
| Sloupec | Typ | Popis |
|---------|-----|-------|
| id | INTEGER | PK |
| session_id | VARCHAR | S1-S8 |
| sender_id | FK | -> User |
| content | TEXT | Zpráva |
| is_optimized | BOOLEAN | AI přepsáno |
| timestamp | DATETIME | Čas |

---

## 10. API Referenční příručka

### REST Endpoints

| Method | Endpoint | Popis |
|--------|----------|-------|
| POST | `/auth/login` | Přihlášení |
| GET | `/auth/logout` | Odhlášení |
| GET | `/api/admin/data/users` | Seznam uživatelů |
| POST | `/api/admin/economy/bonus` | Přidat kredity |
| POST | `/api/admin/economy/fine` | Odebrat kredity |
| POST | `/api/admin/economy/lock` | Zamknout uživatele |
| POST | `/api/admin/tasks/{id}/approve` | Schválit úkol |
| POST | `/api/admin/tasks/{id}/pay` | Vyplatit úkol |
| GET | `/api/admin/controls/state` | Stav ovládacích prvků |
| POST | `/api/admin/root/restart` | Restart serveru |
| POST | `/api/admin/root/factory_reset` | Factory reset |

---

## Přílohy

### A. Diagramy

Diagramy jsou dostupné v souboru `docs/diagrams/` (TODO: vytvořit).

### B. Changelog

Viz `docs/DEVELOPMENT_HISTORY.md`.

---

**Poslední aktualizace:** 2025-12-14
