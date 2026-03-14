# HLINÍK — Audit stavu aplikace

**Datum:** 2026-03-14
**Verze kódu:** Phase 38 (commit 477c0d2)

## Celkový stav

Aplikace je **funkční ale křehká**. Základní flow (login → terminál → WebSocket chat → úkoly → platby) funguje. Řada featur je napůl hotových, dokumentace neodpovídá realitě.

---

## Kritické bugy

### 1. Platby bez transakce
- **Kde:** `app/logic/economy.py`
- **Problém:** Update kreditů usera a treasury probíhají jako nezávislé DB operace. Při selhání uprostřed se rozjedou.
- **Oprava:** Zabalit do jedné DB transakce.

### 2. ~~Panic mode je globální~~ [VYŘEŠENO — design, ne bug]
- **Kde:** `app/logic/gamestate.py`
- **Zjištění:** Manuální panic je per-session (`panic_modes` dict). Automatický panic (`auto_panic_engaged`) je globální — spouští se když teplota > 350°C. To je záměr: přehřátí reaktoru = systémová krize pro všechny. Kód je OK, jen to nebylo jasně zdokumentované.

### 3. ID zmatek (user.id vs logical_id)
- **Kde:** `app/routers/sockets.py`, `app/logic/routing.py`
- **Problém:** Sockets posílá adminům DB `user.id` (auto-increment PK), ale routing používá `logical_id` (1-8). Admin dashboard může zobrazovat špatné session mapování.
- **Oprava:** Sjednotit — buď všude logical_id, nebo explicitní mapování.

### 4. Broadcast platby na špatné ID
- **Kde:** `app/routers/admin_api.py` (~řádek 250)
- **Problém:** `broadcast_to_session(result.get("user_id", action.task_id), ...)` — fallback je `task_id`, což není user_id.
- **Oprava:** Vždy explicitně předat user_id z task objektu.

### 5. Gemini historie oříznutá špatně
- **Kde:** `app/logic/llm_core.py` (~řádek 215)
- **Problém:** `gemini_hist[:-1]` ořezává poslední zprávu z historie. Vypadá jako bug — mělo to asi předejít duplikaci, ale efekt je ztráta kontextu.
- **Oprava:** Ověřit proč se to dělá, opravit nebo odstranit.

### 6. factory_reset přes subprocess
- **Kde:** `app/routers/admin_api.py`
- **Problém:** Maže DB soubory přes subprocess s race conditions. Pokud selže, systém může zůstat v nekonzistentním stavu.
- **Oprava:** Použít Python os/shutil, ošetřit chyby.

---

## Napůl implementované featury

| Feature | Soubor | Stav | Poznámka |
|---------|--------|------|----------|
| ~~Simulation API~~ | `routers/simulation.py` | ~~Nefunkční~~ OK | Modul se importuje, simulace funkční |
| Lore Editor API | `routers/lore_editor_api.py` | Backend OK, frontend chybí | CRUD endpointy existují, edituje se přes lore-web |
| ~~FORENSIC mode~~ | sockets, chat_service, admin_service | ~~Nepoužitý~~ IMPLEMENTOVÁNO | Skryje živé HYPER zprávy, zobrazí historii při reconnectu |
| ~~EPHEMERAL mode~~ | sockets, chat_service, admin_service | ~~Duplicitní~~ IMPLEMENTOVÁNO | Zobrazí živé HYPER, skryje historii; přidáno do admin UI + překlady |
| ~~IRIS překlad~~ | `routers/translations.py` | ~~Nefunkční~~ OK | `iris.json` existuje v `app/translations/`, mód `czech-iris` implementován |
| ~~llm_tools.py~~ | ~~`logic/llm_tools.py`~~ | ~~Mrtvý kód~~ SMAZÁNO | Prázdná třída odstraněna |

---

## Nekonzistence a technický dluh

### ~~Verze~~ [OPRAVENO]
- ~~`config.py` → `VERSION = "1.0.0"`~~ → Sjednoceno na "3.1.2"

### ~~Konfigurace~~ [OPRAVENO]
- ~~`DEFAULT_CHERNOBYL_VALUE`~~ a ~~`DEFAULT_HYPER_VISIBILITY`~~ — odstraněny z config.py

### Bezpečnost
- Auth cookie má `httponly=False` — token čitelný JavaScriptem
- Žádná revokace tokenů — zamčený user zůstane přihlášený do expirace (24h)
- `get_lore_data` nemá validaci cesty — potenciální path traversal
- Hesla v `seed.py` hardcoded (OK pro dev, ale seed běží vždy)

### LLM
- `AsyncOpenAI` klient se vytváří na každý request — měl by se cachovat
- `evaluate_submission` parsuje číslo z textu regexem — pokud model odpoví slovně, default 50
- `rewrite_message` ignoruje system_prompt z configu, má hardcoded vlastní
- Žádný rate limiting / quota handling

### Testy
- `conftest.py` má 11 řádků — žádné DB/auth fixtures
- Testy míchají unit, integration, E2E v jednom adresáři
- `verify_*.py` skripty nejsou pytest testy
- Žádná testovací databáze

### Frontend
- `admin_ui.js` — 1543 řádků imperativní DOM manipulace
- Žádná input sanitizace v chatu — potenciální XSS z LLM odpovědí
- API cesty hardcoded v JS

---

## Co funguje dobře

- **Auth flow** — JWT + bcrypt, role-based přístup (USER/AGENT/ADMIN/ROOT)
- **WebSocket** — heartbeat, reconnect s jitter, message persistence před broadcast
- **GameState singleton** — export/import do JSON, bounds checking
- **Session izolace** — 8 paralelních sessions, shift rotation pro agenty
- **Ekonomika** — základní flow (task → submit → rate → pay) funguje
- **Multi-provider LLM** — OpenAI, Gemini, OpenRouter s fallback na mock
- **Dispatcher pattern** — čisté routování zpráv přes services

---

## Prioritní plán oprav

1. **Kritické bugy** (#1-6 výše)
2. **Mrtvý kód a nekonzistence** (llm_tools.py, verze, config konstanty)
3. **Napůl hotové featury** — rozhodnout per feature: doimplementovat nebo smazat
4. **Bezpečnost** — httponly cookie, token revokace, path traversal
5. **Test infrastruktura** — fixtures, testovací DB, organizace testů
