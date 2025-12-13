# Development Log - IRIS v1.4: Power Cap & Admin Economy

**Date:** 2025-12-13
**Version:** v1.4 Specification

## Zadání (Specification)

### 1. Power Management (Řízení Výkonu)
**Logika:** Capacity (Limit) vs. Load (Spotřeba).
-   **Capacity**: Nastavuje ROOT (např. 100 MW).
-   **Load**: Součet procesů:
    -   Base Load (OS): 10 MW
    -   Active Terminal: 2 MW/ks
    -   Optimizer: +5 MW
    -   Hyper Mode: +10 MW (per autopilot)
    -   Low Latency: +30 MW
-   **Overload (Brownout)**: Pokud Load > Capacity -> Glitch Protocol pro USER (instability-max, Zalgo text, network errors). Admin UI OK.
-   **Power Packs**: Admin může koupit "Emergency Generator" (+50 MW na 30 min) za 1000 CR z Admin Poolu.

### 2. Latency & Agent Timer
**Logika**: Hard time limit pro odpověď Agenta.
-   **Modes**: Real-time (30s), Standard (2 min), Deep Space (10 min).
-   **Dopad**: Pokud Agent nestihne -> Input lock -> Zpráva uživateli "Connection Timeout". Uživatel musí psát znovu.

### 3. Společná Ekonomika Správců (The Treasury)
-   **Admin Tax**: % z odměny za Task jde do Admin Poolu (default 10%).
-   **Výdaje**: Power Packs, Unlocky.
-   **UI**: Zobrazení Balance, Income Rate, Histograf v Dashboardu.

### 4. Custom Labels
-   **Funkce**: Admin může přejmenovat ovládací prvky (Roleplay).
-   **Tech**: `admin_labels.json`. Edit Mode v Dashboardu.

---

## Postup Vývoje (Progress Log)

### Fáze 1: Analýza a Plánování
- [x] Vytvoření tohoto logu.
- [ ] Aktualizace `task.md` a `implementation_plan.md`.

### Fáze 2: Backend Core (Power & Economy)
- [ ] `gamestate.py`: Implementace `PowerManager` (Load calc) a `AgentTimer`.
- [ ] `economy.py` (New? or `admin_api.py` logic): Implementace `AdminTreasury`.

### Fáze 3: API & Sockets
- [ ] `slots`: Glitch event trigger.
- [ ] `admin_api`: Endpoints pro Power, Timer, Labels.

### Fáze 4: Frontend Implementation
- [ ] `dashboard.html`: Power UI, Treasury UI, Label Editor.
- [ ] `agent_terminal.html`: Timer Bar.
- [ ] `user_terminal.html`: Glitch Effects (Zalgo).

### Fáze 5: Verifikace
- [ ] Test Scénář: Overload -> User Glitch.
- [ ] Test Scénář: Task Complete -> Tax -> Admin Pool Increase.
- [ ] Test Scénář: Timer Timeout -> Agent Lock.
