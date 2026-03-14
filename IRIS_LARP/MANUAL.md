# HLINÍK — Kompletní návod

**Verze:** 3.1.2 | **Phase:** 38 | **Datum:** 2026-03-14

Tento dokument je **závazná specifikace** aplikace HLINÍK. Kód musí odpovídat tomuto návodu. Pokud se návod a kód rozcházejí, návod má přednost a kód se opraví.

---

## 1. Přehled systému

HLINÍK je webová aplikace pro LARP hru IRIS. Simuluje dystopický korporátní systém, kde subjekty (hráči) komunikují s agenty (operátory) přes terminály. Správci ovládají herní mechaniky.

### 1.1 Role

| Role | Uživatelé | Popis |
|------|-----------|-------|
| **Subjekt (User)** | user1–user8 | Hráč. Komunikuje s agentem, plní úkoly, získává kredity. |
| **Agent (Operátor)** | agent1–agent8 | Odpovídá subjektům. Může zapnout autopilota (AI odpovídá místo něj). |
| **Správce (Admin)** | admin1–admin4 | Ovládá herní mechaniky: shift, teplotu, ekonomiku, úkoly. |
| **ROOT** | root | Gamemaster. Má přístup ke všemu + konfigurace AI, server restart, factory reset. |

### 1.2 Sessions

Systém má 8 paralelních sessions (S1–S8). Každý subjekt je napevno přiřazen k jedné session (user1 = S1, user2 = S2, ...). Agenti rotují přes shift mechanismus.

**Přiřazení agenta k session:**
```
session = ((agent_číslo - 1) + shift) % 8 + 1
```
Příklad: Při shift=0 je agent1 na S1, agent2 na S2. Při shift=1 je agent1 na S2, agent2 na S3, atd.

### 1.3 Technologie

- Backend: FastAPI (Python), SQLite, WebSocket
- Frontend: Vanilla JS + Jinja2 šablony, žádný framework
- LLM: OpenAI, Gemini, OpenRouter (konfigurovatelné)

---

## 2. Přihlášení

### 2.1 Přihlašovací obrazovka

Adresa: `http://<server>:8000`

1. Pole **IDENTIFIKÁTOR** — uživatelské jméno
2. Pole **HESLO** — heslo
3. Tlačítko **INICIOVAT RELACI** — přihlásit

Po přihlášení systém automaticky přesměruje na správný terminál podle role.

### 2.2 Testovací režim

Když ROOT zapne testovací režim, na přihlašovací stránce se zobrazí rychlá tlačítka pro přihlášení bez hesla. Barvy tlačítek odpovídají rolím.

### 2.3 Výchozí přihlašovací údaje

| Role | Uživatel | Heslo |
|------|----------|-------|
| ROOT | root | master_control_666 |
| Admin | admin1–4 | secure_admin_1–4 |
| Agent | agent1–8 | agent_pass_1–8 |
| User | user1–8 | subject_pass_1–8 |

Počáteční kredity subjektů: 100.

---

## 3. Terminál subjektu (User)

Zelený terminál. Levý panel = stav + úkoly, pravý panel = chat.

### 3.1 Stavové informace

- **POSUN SVĚTA** — aktuální shift (0–7), určuje přiřazení agenta
- **KREDITY** — virtuální měna, získává se za úkoly, ztrácí se za pokuty

### 3.2 Úkoly

**Tlačítko [ + VYŽÁDAT ]** — požádá o nový úkol. Úkol musí schválit správce.

**Životní cyklus úkolu:**

| Stav | Zobrazení | Co může subjekt dělat |
|------|-----------|----------------------|
| PENDING_APPROVAL | "ČEKÁ NA SCHVÁLENÍ" (žlutá) | Čekat |
| ACTIVE | "ZADÁNO" (modrá) | Napsat odpověď a kliknout ODEVZDAT |
| SUBMITTED | "ODEVZDÁNO" (zelená) | Čekat na hodnocení |
| PAID | "ZAPLACENO" (šedá) | Vidí výplatu a rating |

**Odměna za úkol:**
```
odměna = nabídka × (rating / 100)
daň = odměna × sazba_daně
čistá_výplata = odměna - daň
```
Daň jde do Treasury (společná pokladna správců).

### 3.3 Chat

- Zprávy od agenta se zobrazují v chatu
- Vstupní pole + tlačítko **ODESLAT** (nebo Enter)
- **Tlačítko [ ! ] (Report)** — nahlásí zprávu agenta jako anomálii. Každý report zvýší teplotu systému o 15°C. Zprávy s badge **VERIFIED** (přepsané optimizerem) nelze reportovat.

### 3.4 Indikátor psaní

Když agent píše, zobrazí se indikátor. Subjekt také posílá svůj typing status agentovi.

### 3.5 Speciální stavy

**Purgatory (záporné kredity):**
- Chat je zablokován, zobrazí se červený overlay "COMMUNICATION OFFLINE due to Debt"
- Subjekt stále může žádat o úkoly a odevzdávat je
- Po vyrovnání kreditů se terminál odemkne

**Glitch režim (systém přetížen):**
- Obrazovka se třese a mění barvy
- Herní efekt signalizující přetížení systému

### 3.6 Témata

Vizuální téma terminálu se mění podle status_level subjekta (low/mid/high/party). Status nastavuje správce.

### 3.7 Zvuk

Posuvník hlasitosti (0–100%) v pravém panelu. Zvukové efekty: příjem zprávy, odeslání, chyba.

### 3.8 Manuál a odhlášení

- Tlačítko **MANUÁL** — otevře in-app dokumentaci
- Tlačítko **ODHLÁSIT** — odhlásí ze systému

---

## 4. Terminál agenta (Agent)

Růžový/magenta terminál. Levý panel = status + timer, pravý panel = chat.

### 4.1 Stavové informace

- **AGENT** — jméno (např. AGENT3)
- **ID RELACE** — session, ke které je přiřazen (např. S1)
- **SHIFT** — aktuální shift hodnota
- **TEPLOTA** — teplota systému v °C
- **OKNO** — deadline pro odpověď v sekundách
- **LLM** — stav připojení k AI (ONLINE/OFFLINE)

### 4.2 Časovač odpovědi

- Žlutý pruh ukazuje zbývající čas
- Červená když < 20% času
- Když čas vyprší: vstup se zablokuje, subjekt dostane notifikaci "Agent neodpovídá"
- Reset: po odeslání zprávy, nebo když subjekt pošle novou zprávu

### 4.3 Chat

- Zprávy od přiřazeného subjekta se zobrazují automaticky
- Vstupní pole + tlačítko **TRANSMIT** (nebo Enter)

### 4.4 AI Optimizer

Když správce zapne optimizer:
1. Agent napíše zprávu a odešle
2. Zobrazí se loader "PROBÍHÁ OPTIMALIZACE..."
3. AI přepíše zprávu do korporátního tónu
4. Agent vidí náhled: ~~původní text~~ → nový text (zeleně)
5. Agent klikne **POTVRDIT** nebo **ODMÍTNOUT**
6. Potvrzená zpráva dostane badge VERIFIED (nelze ji reportovat)

### 4.5 HYPER-MÓD (Autopilot)

Toggle přepínač na levém panelu. Když je zapnutý:
- Obrazovka se zamkne, zobrazí se "HYPER-VISIBILITY AKTIVNÍ"
- AI odpovídá místo agenta na zprávy subjektů
- Pro odemčení: zadat heslo (uživatelské jméno agenta nebo `master_control_666`)
- Při vypnutí se historie HYPER konverzace vymaže

### 4.6 Visibility módy

Správce může přepnout visibility mód, který ovlivňuje co agent vidí:

| Mód | Živé HYPER zprávy | Historie při reconnectu | Vizuální efekt |
|-----|-------------------|------------------------|----------------|
| **NORMAL (STD)** | Ano | Ano | Žádný |
| **EPHEMERAL (EPH)** | Ano | Ne | Italic + průhlednost |
| **BLACKBOX (RAW)** | Ne | Ne | Blur + ztmavení |
| **FORENSIC (SCAN)** | Ne | Ano | Sépiový filtr |

- **NORMAL** — agent vidí vše transparentně
- **EPHEMERAL** — agent vidí živé HYPER zprávy, ale při reconnectu je historie prázdná ("zapomeň co jsi viděl")
- **BLACKBOX** — agent nevidí nic z HYPER činnosti, ani živě ani v historii
- **FORENSIC** — agent nevidí živé HYPER zprávy, ale při reconnectu se mu odhalí celá historie ("máme důkazy")

### 4.7 Speciální stavy

**Timeout (vstup zamčen):**
- Overlay "INPUT LOCKED - Connection timeout"
- Subjekt musí poslat novou zprávu

**Overload signál:**
- V rohu se objeví "SYSTEM OVERLOAD"

---

## 5. Dashboard správce (Admin)

Modrý/cyan terminál. Hub se 4 stanicemi.

### 5.1 Hub

4 klikatelné dlaždice:

| # | Stanice | Kódový název | Barva | Funkce |
|---|---------|-------------|-------|--------|
| 01 | MONITORING | UMYVADLO | Zelená | Sledování všech relací |
| 02 | KONTROLA | ROZKOŠ | Žlutá | Herní nastavení |
| 03 | EKONOMIKA | BAHNO | Modrá | Správa kreditů |
| 04 | ÚKOLY | MRKEV | Fialová | Schvalování a vyplácení |

Kódové názvy jsou výchozí — správce je může přejmenovat přes "PŘEPSAT REALITU".

### 5.2 Stanice MONITORING

4 záložky:

**VŠEVIDOUCÍ** — mřížka všech 8 sessions. Každá karta ukazuje posledních N zpráv. Vpravo mini-log systémových událostí.

**ŠUM** — pouze chat karty bez logu.

**HISTORIE OMYLŮ** — kompletní systémový log. Tlačítko "VYMAZAT HISTORII" smaže log.

**PAVUČINA** — síťový graf relací (experimentální).

### 5.3 Stanice KONTROLA

**POSUN REALITY (Shift):**
- Zobrazuje aktuální shift
- Tlačítko **ROZTOČIT KOLA OSUDU** — zvýší shift o 1

**TLAK PÁRY (Power):**
- Modrý pruh: load / capacity
- Tlačítko **PŘIHODIT UHLÍ** — +50 MW na 30 minut, stojí 1000 CR z Treasury
- Pokud je boost aktivní, zobrazí se odpočet

**HLADINA STRESU (Teplota):**
- Barevný pruh od zelené (20°C) po červenou (350°C+)
- Manuální posuvník pro ruční nastavení
- 3 režimy teploty:

| Režim | Rozpad za tick | Popis |
|-------|---------------|-------|
| **NORMÁL** | -0.5°C | Výchozí provoz |
| **ÚSPORA** | -1.5°C | Rychlé chlazení |
| **PŘETÍŽENÍ** | +0.1°C | Teplota pomalu roste |

Teplota roste při: reportech anomálií (+15°C), manuálním ohřevu (+2.5°C), overclockingu.

Při překročení 350°C se automaticky aktivuje globální panic mode (cenzura zpráv pro všechny sessions).

**FILTR PRAVDY (Visibility):**
- 4 tlačítka: STD / EPH / RAW / SCAN
- Ovlivňuje co agenti vidí (viz sekce 4.6)

**PANIC (per-session):**
- Manuální panic pro konkrétní session + roli (user/agent)
- Zapne LLM cenzuru — zprávy se přepíší do neutrálního textu

### 5.4 Stanice EKONOMIKA

**NÁRODNÍ BANKA BAHNA** — zobrazuje Treasury balance.

**Tabulka uživatelů:**
- Sloupce: Jméno, Kredity, Status, Locked
- Akce per uživatel:

| Tlačítko | Funkce |
|----------|--------|
| **[+]** | Přidat kredity (bonus) |
| **[-]** | Odebrat kredity (pokuta) |
| **[LOCK]** | Zamknout terminál (Purgatory) |
| **[UNLOCK]** | Odemknout terminál |

- Status level (low/mid/high/party) se nastavuje zde — ovlivňuje vizuální téma a výchozí odměnu za úkoly

### 5.5 Stanice ÚKOLY

**Seznam všech úkolů** od subjektů.

**Akce:**

| Tlačítko | Kdy | Funkce |
|----------|-----|--------|
| **APPROVE** | PENDING_APPROVAL | Schválí úkol, nastaví odměnu, volitelně edituje popis |
| **PAY** | SUBMITTED | Vyplatí odměnu. Rating: 0% / 50% / 100% / 200% |

Při schválení úkolu může AI vygenerovat popis (pokud admin nezadá vlastní).

**Výchozí odměny podle status_level:**

| Status | Odměna |
|--------|--------|
| low | 75 CR |
| mid | 125 CR |
| high | 175 CR |
| party | 200 CR |
| default | 100 CR |

### 5.6 Horní lišta

- **PŘEPSAT REALITU** — editační režim pro přejmenování UI prvků (klikni na text → přepiš → uloží se)
- **MODZEK (AI Config)** — modální okno pro optimizer prompt a autopilot model
- **AUTO-DESTRUKCE** — system reset (vyžaduje potvrzení)
- **ODHLÁSIT** — odhlášení

---

## 6. ROOT konzole

Zlatý/černý dashboard. Má všechny admin funkce + navíc:

### 6.1 Záložky

| Záložka | Obsah |
|---------|-------|
| **DASHBOARD** | System status, physics constants, executive protocols, system log |
| **CONFIG** | Test mode, jazyk, AI konfigurace |
| **ECONOMY** | Globální manipulace s kredity |
| **CHRONOS** | Ruční nastavení shiftu |
| **PANOPTICON** | Surveillance grid (8x8 raw chat) |
| **SIMULATION** | LLM hodinová simulace |
| **LORE** | Embed lore-web wiki |

### 6.2 Dashboard

**System Status:** shift offset, online users, teplota.

**Physics Constants:**
- TAX RATE (0.0–1.0) — výchozí 0.20
- POWER CAP (MW) — výchozí 100
- TEMP THRESHOLD — výchozí 350°C
- TEMP RESET VALUE — výchozí 80°C
- TEMP MIN — výchozí 20°C
- Náklady: BASE, PER_USER, PER_AUTOPILOT, LOW_LATENCY, OPTIMIZER
- Odměny za úkoly: default, low, mid, high, party
- Tlačítko **APPLY PHYSICS** — uloží změny

**Executive Protocols:**

| Tlačítko | Funkce | Potvrzení |
|----------|--------|-----------|
| **FORCE SHIFT** | Shift +1 | Ne |
| **GLOBAL BROADCAST** | Zpráva všem | Ne |
| **SYSTEM RESET** | Soft reset (kredity na 100, smaže logy + úkoly, zachová DB) | "NUKE" |
| **RELOAD UI** | Refresh stránky | Ne |
| **RESTART SERVER** | Kill + restart Python procesu (~5s výpadek) | Ne |
| **FACTORY RESET** | Smaže DB + gamestate.json + labels, restart | "FACTORY RESET" |

### 6.3 Config

**Test Mode** — toggle, zapne quick-login tlačítka.

**Jazyk:**
- Čeština (výchozí)
- English
- Crazy Čeština (zábavné alternativní texty)
- Čeština + IRIS Terminologie (lore-specifická terminologie)

**AI Configuration:**
- OPTIMIZER PROMPT — textový prompt pro přepisování zpráv
- AUTOPILOT MODEL — výběr modelu
- API klíče (OpenAI, OpenRouter)

### 6.4 Simulation

Spouští LLM hodinovou simulaci (automatizované testování systému). Módy:
- SHORT TEST — 5 minut
- FULL — 1 hodina

Status: IDLE / RUNNING / COMPLETED / FAILED. Logy a historie přístupné přes API.

---

## 7. Herní mechaniky

### 7.1 Teplota

- Rozsah: 20°C (min) – 1000°C (max)
- Výchozí: 80°C
- Klesá každý tick (1 sekunda) podle režimu: NORMAL -0.5, LOW_POWER -1.5, OVERCLOCK +0.1
- Roste při: reportech (+15), manuálním ohřevu (+2.5)
- Threshold 350°C = automatický panic (globální cenzura)

### 7.2 Power

- Kapacita: výchozí 100 MW
- Load = BASE + (PER_USER × aktivní terminály) + (PER_AUTOPILOT × autopiloti) + (LOW_LATENCY if active) + (OPTIMIZER if active)
- Overload: load > capacity NEBO teplota > threshold
- Boost: +50 MW na 30 minut za 1000 CR z Treasury

### 7.3 Ekonomika

- Každý subjekt začíná se 100 CR
- Treasury začíná s 500 CR
- Výdělky: za splněné úkoly (odměna × rating%, minus daň)
- Ztráty: pokuty od správce
- Záporné kredity = Purgatory (chat blokován)
- Daň (výchozí 20%) jde do Treasury

### 7.4 Shift

- Rozsah: 0–7
- Mění přiřazení agentů k sessions
- Správce/ROOT může zvýšit o 1 nebo nastavit ručně
- Všichni připojení klienti dostanou update

### 7.5 Panic mode

**Automatický (globální):** Teplota > 350°C → všechny zprávy všech sessions se cenzurují přes LLM.

**Manuální (per-session):** Správce může zapnout panic pro konkrétní session + roli (user/agent). Cenzurují se jen zprávy dané role v dané session.

---

## 8. LLM integrace

### 8.1 Poskytovatelé

| Poskytovatel | API klíč (env) | Použití |
|-------------|----------------|---------|
| OpenAI | OPENAI_API_KEY | Task evaluator (gpt-4o) |
| OpenRouter | OPENROUTER_API_KEY | Autopilot, Optimizer, Censor (gemini-2.5-flash-lite) |
| Gemini | GEMINI_API_KEY | Alternativní přímý přístup |

Pokud klíč chybí, LLM vrací mock odpovědi.

### 8.2 Role LLM

| Role | Účel | Výchozí model |
|------|------|---------------|
| **Task Evaluator** | Hodnocení odevzdaných úkolů | gpt-4o (OpenAI) |
| **HYPER/Autopilot** | Automatické odpovědi místo agenta | gemini-2.5-flash-lite (OpenRouter) |
| **Optimizer** | Přepis zpráv agentů do korporátního tónu | gemini-2.5-flash-lite (OpenRouter) |
| **Censor** | Sanitizace zpráv v panic mode | gemini-2.5-flash-lite (OpenRouter) |

Všechny systémové prompty jsou v češtině a reflektují korporátní tón HLINÍK a syn s.r.o.

---

## 9. WebSocket protokol

Veškerá real-time komunikace probíhá přes WebSocket na `/ws/connect?token=<JWT>`.

### 9.1 Heartbeat

Klient posílá `{"type": "ping"}` periodicky, server odpovídá `{"type": "pong"}`.

### 9.2 Zprávy server → klient

| Typ | Příjemci | Obsah |
|-----|----------|-------|
| `gamestate_update` | Všichni | shift, temperature, is_overloaded, hyper_mode, agent_window |
| `user_status` | User | credits, is_locked, shift |
| `task_update` | User | task_id, status, description, reward, submission, rating |
| `system_alert` | Všichni | Overlay zpráva (failover, reset) |
| `agent_timeout` | User | Agent neodpovídá |
| `report_accepted` | User | Anomálie zalogována |
| `report_denied` | User | Zpráva ověřená, nelze reportovat |
| `optimizing_start` | Session | Loader pro optimizer/autopilot |
| `optimizer_preview` | Agent | original + rewritten text |
| `status_update` | Admini | user online/offline notifikace |
| `admin_refresh_tasks` | Admini | Signál pro refresh seznamu úkolů |
| `labels_update` | Non-admini | Aktualizované custom labely |
| `language_change` | Všichni | Změna jazyka |

### 9.3 Zprávy klient → server

| Typ | Odesílatel | Obsah |
|-----|-----------|-------|
| `ping` | Všichni | Heartbeat |
| (chat) | User/Agent | `{ content }` — prostý text zprávy |
| `task_request` | User | Žádost o úkol |
| `task_submit` | User | `{ task_id, content }` |
| `report_message` | User | `{ id }` — ID zprávy |
| `autopilot_toggle` | Agent | `{ status: true/false }` |
| `typing_sync` | User/Agent | `{ content }` — sync across tabs |
| `typing_start/stop` | User/Agent | Typing indicator |
| `confirm_opt` | Agent | `{ content, confirm_opt: true }` — potvrzení optimizace |

---

## 10. REST API

### 10.1 Auth

| Metoda | Cesta | Popis |
|--------|-------|-------|
| GET | `/auth/login` | Přihlašovací stránka |
| POST | `/auth/login` | Přihlášení (username + password) |
| GET | `/auth/logout` | Odhlášení |
| GET | `/auth/terminal` | Redirect na terminál podle role |
| GET | `/auth/me` | Info o aktuálním uživateli |

### 10.2 Admin API (`/api/admin/`)

| Metoda | Cesta | Popis |
|--------|-------|-------|
| GET | `llm/config` | Čtení LLM konfigurací |
| POST | `llm/config/{type}` | Nastavení LLM (task/hyper/optimizer/censor) |
| GET | `llm/keys` | Maskované API klíče (ROOT only) |
| GET | `data/users` | Seznam uživatelů |
| POST | `economy/fine` | Pokuta |
| POST | `economy/bonus` | Bonus |
| POST | `economy/toggle_lock` | Zamknout/odemknout |
| POST | `economy/set_status` | Změna status_level |
| POST | `economy/global_bonus` | Bonus všem |
| POST | `economy/reset` | Reset ekonomiky |
| GET | `tasks` | Seznam úkolů |
| POST | `tasks/approve` | Schválení úkolu |
| POST | `tasks/grade` | Hodnocení (modifier: 0.0/0.5/1.0/2.0) |
| POST | `tasks/pay` | Vyplacení (rating: 0/50/100/200) |
| POST | `optimizer/toggle` | Zapnout/vypnout optimizer |
| POST | `optimizer/prompt` | Nastavit optimizer prompt |
| GET | `controls/state` | Celý gamestate |
| POST | `timer` | Nastavit response window |
| POST | `power/buy` | Koupit power boost (1000 CR) |
| GET/POST | `labels` | Custom UI labels |
| POST | `debug/treasury` | Ručně nastavit Treasury |
| GET | `system_logs` | Systémové logy (posledních 100) |
| POST | `root/update_constants` | Nastavení physics (ROOT) |
| GET | `root/state` | Kompletní stav pro ROOT |
| GET/POST | `root/ai_config` | AI konfigurace (ROOT) |
| POST | `root/reset` | System reset (ROOT) |
| POST | `root/restart` | Server restart (ROOT) |
| POST | `root/factory_reset` | Factory reset (ROOT) |

### 10.3 Translations API (`/api/translations/`)

| Metoda | Cesta | Popis |
|--------|-------|-------|
| GET | `/` | Překlady pro aktuální jazyk |
| POST | `/language` | Změna jazyka (ROOT only) |
| POST | `/label` | Nastavení custom labelu |
| DELETE | `/label/{key}` | Smazání custom labelu |
| POST | `/reset-labels` | Reset všech custom labelů |
| GET | `/language-options` | Dostupné jazyky |
| GET | `/files/list` | Seznam překladových souborů |
| GET | `/files/{code}` | Obsah překladového souboru |
| POST | `/files/{code}` | Uložení překladového souboru |

### 10.4 Lore Editor API (`/api/lore-editor/`)

CRUD operace nad JSON soubory lore-web:

| Metoda | Cesta | Popis |
|--------|-------|-------|
| GET | `/files` | Seznam editovatelných souborů |
| GET | `/file/{key}` | Obsah souboru |
| PUT | `/file/{key}` | Uložení celého souboru |
| GET | `/file/{key}/records` | Seznam záznamů |
| GET | `/file/{key}/record/{id}` | Detail záznamu |
| PUT | `/file/{key}/record/{id}` | Update záznamu |
| POST | `/file/{key}/record` | Nový záznam |
| DELETE | `/file/{key}/record/{id}` | Smazání záznamu |
| GET | `/references/{id}` | Hledání referencí na ID |
| GET | `/schema/{key}` | Auto-detekce schématu |

Editovatelné soubory: users, tasks, relations, abilities, task_types, relation_types, story_nodes, roles, config.

### 10.5 Simulation API (`/api/admin/simulation/`)

| Metoda | Cesta | Popis |
|--------|-------|-------|
| GET | `/status` | Stav simulace (ROOT) |
| POST | `/start` | Spuštění (ROOT) |
| POST | `/stop` | Zastavení (ROOT) |
| GET | `/logs` | Logy simulace (ROOT) |
| GET | `/history` | Historie běhů (ROOT) |

---

## 11. Databáze

SQLite. Modely:

### User
| Pole | Typ | Popis |
|------|-----|-------|
| id | int (PK) | Auto-increment |
| username | string | Unikátní |
| password_hash | string | bcrypt |
| role | UserRole | USER / AGENT / ADMIN |
| credits | int | Výchozí 100 |
| status_level | string | low / mid / high / party |
| is_locked | bool | Purgatory stav |

### ChatLog
| Pole | Typ | Popis |
|------|-----|-------|
| id | int (PK) | |
| session_id | int | 1–8 |
| sender_id | int (FK→User) | |
| content | string | Text zprávy |
| timestamp | datetime | |
| is_hyper | bool | Zpráva od autopilota |
| is_optimized | bool | Přepsáno optimizerem (immune to reports) |
| was_reported | bool | Nahlášeno subjektem |

### Task
| Pole | Typ | Popis |
|------|-----|-------|
| id | int (PK) | |
| user_id | int (FK→User) | |
| prompt_desc | string | Popis úkolu |
| reward_offered | int | Nabídnutá odměna |
| status | TaskStatus | PENDING_APPROVAL / ACTIVE / SUBMITTED / COMPLETED / PAID |
| submission_content | string | Odevzdaná odpověď |
| final_rating | int | Hodnocení (0–200) |

### SystemConfig
Key-value store pro runtime konfiguraci.

### SystemLog
Event log (timestamp, event_type, message, data).

---

## 12. Spuštění a konfigurace

### 12.1 Instalace

```bash
cd IRIS_LARP
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 12.2 Konfigurace

Soubor `.env` v adresáři `IRIS_LARP/`:

```env
SECRET_KEY=<bezpečný-náhodný-řetězec>
OPENAI_API_KEY=<klíč>
OPENROUTER_API_KEY=<klíč>
GEMINI_API_KEY=<klíč>
```

### 12.3 Spuštění

```bash
# Z kořene repa:
python IRIS_LARP/run.py

# Nebo z IRIS_LARP/:
./run.sh          # aktivuje venv, zabije port 8000, spustí
```

Server běží na `http://0.0.0.0:8000`.

### 12.4 Game loop

Běží na pozadí každou sekundu:
1. Tick teploty (decay podle režimu)
2. Výpočet power load
3. Kontrola overloadu
4. Broadcast gamestate_update pokud se stav změnil

### 12.5 Persistence

GameState se exportuje do `data/gamestate.json` při shutdown a importuje při startu. Pokud se proces zabije (SIGKILL), stav se ztratí.

---

## 13. Známé omezení

1. **Žádné DB migrace** — změna schématu vyžaduje factory reset
2. **SQLite only** — není pro produkční multi-process provoz
3. **Token bez revokace** — zamčený/smazaný user zůstane přihlášený do expirace (24h)
4. **Žádný rate limiting** na LLM API
5. **httponly=false** na auth cookie
