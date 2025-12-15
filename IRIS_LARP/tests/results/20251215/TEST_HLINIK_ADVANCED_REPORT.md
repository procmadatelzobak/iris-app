# Phase 36B: HLINIK Advanced Sync & Purgatory Recovery

**Datum/čas:** 15. 12. 2025 17:10 CET  
**Tester:** Automation Agent (HLINIK)  
**Cíl:** Ověřit pokročilé, doposud netestované funkce – reálný čas směn, průchod purgatory recovery platbou, kolize optimizer/autopilot a ROOT broadcast/test-mode.

## Zadání
- Pokrýt mezery po Phase 35/36: realtime shift, debt lockout & recovery payment, optimizer+autopilot lock, ROOT broadcast latence.
- Výsledky musí být publikovány v organizer-wiki (`/doc/iris/lore-web/data/test_runs`).
- Zachytit obrazové důkazy.

## Prostředí
- Server: localhost:8000 (simulovaný test mód)
- Databáze: SQLite (in-memory pro unit testy), Session injection pro payment flow
- Kódová větev: `copilot/add-advanced-test-scenario`

## Průběh testu
1. Spuštění advanced scénáře (Phase 36B) podle `TEST_AUTO_HLINIK_WORKFLOW.md` s důrazem na netestované části.
2. Shift rotation na admin stanici → ověřena propagace na agent a panoptikon (500 ms).
3. Ekonomika: pokuta do mínusu → recovery task → zaplacení s ratingem 100 % → odemknutí purgatory.
4. AI nástroje: optimizer běžel paralelně s přepínaným autopilotem, kontrola zámků a immunity.
5. ROOT: zapnutí test-mode quick login, broadcast na všechny role, měření latence (~2 s varování).

## Výsledky
- **Status:** PASS (4/4 testů), 1 warning (broadcast delay)
- **Evidence (screenshots):**
  - `doc/iris/lore-web/data/test_runs/runs/hlinik_shift_sync.png`
  - `doc/iris/lore-web/data/test_runs/runs/hlinik_purgatory_recovery.png`
  - `doc/iris/lore-web/data/test_runs/runs/hlinik_optimizer_lock.png`
  - `doc/iris/lore-web/data/test_runs/runs/hlinik_testmode_broadcast.png`
- **Logy:** uložené v `doc/iris/lore-web/data/test_runs/runs/manual_test_hlinik_advanced.json`

## Nalezený problém
- **BUG-HLINIK-ECON-SESSION (HIGH):** `process_task_payment` vždy otevíral vlastní `SessionLocal`, což v izolovaných scénářích vracelo `{ "error": "Task not found" }` a chyběl `status`. Ověřeno v recovery flow.

## Oprava
- Přidán volitelný parametr `db` do `process_task_payment`, sdílí transakci volajícího a zavírá pouze vlastní session. 
- Aktualizovány testy `test_hlinik_economy.py` a `test_hlinik_economy_raw.py` k injektování session.

## Úspěšné testy po opravě
- `python -m pytest IRIS_LARP/tests/test_hlinik_economy.py -q`
- `python -m pytest IRIS_LARP/tests/test_hlinik_economy_raw.py -q`

## Závěr a doporučení
- Advanced workflow je nyní kompletně pokryt a viditelný v organizer-wiki (Phase 36B položka).
- Doporučení: měřit latenci broadcastů a zpřístupnit session injection i v admin API pro hromadné platby.
