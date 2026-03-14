# Lore-Web — Audit stavu aplikace

**Datum:** 2026-03-14
**Verze kódu:** 4.2.0 / Phase 38

## Celkový stav

Aplikace je **funkční a stabilní**. Většina featur funguje, offline režim spolehlivý. Hlavní problémy jsou nekonzistentní verze v UI a pár nedokončených featur.

---

## Co funguje

- Dashboard se statistikami
- Role definitions (4 role s detailními popisy)
- Users/Players grid s avatary a briefings
- Interaktivní graf vztahů (canvas, vlastní fyzika, 14 typů vztahů)
- Seznam vztahů s filtrováním
- Timeline (6 fází, 18+ událostí)
- Feature tabulka (240 HLINÍK featur s filtrováním)
- LLM Prompts zobrazení + kopírování
- PDF export (jednotlivé briefings, bulk ZIP, manuály)
- Test viewer (historie testů)
- JSON Editor / Lore Editor (plný CRUD přes HLINÍK API)
- Offline režim (fallback na embedded data)
- Print support

---

## Problémy

### Nekonzistentní verze v UI

6 různých verzí/fází na různých místech v index.html:

| Místo | Verze | Fáze |
|-------|-------|------|
| config.json / meta.json | 4.2.0 | 38 |
| HTML title | IRIS 4.1 | Phase 38 |
| Header brand | IRIS 4.2 | — |
| Dashboard karta | IRIS 4.0 | Phase 38 |
| Graf vztahů subtitle | IRIS 4.2 | Phase 37 |
| Systémové docs subtitle | IRIS 4.1 | Phase 35 |
| app.js hlavička | IRIS 4.1 | Phase 35 |

**Oprava:** Sjednotit na jednu verzi, ideálně číst z meta.json.

### Nedokončené featury

| Feature | Stav | Poznámka |
|---------|------|----------|
| **Generators modul** | Neimplementováno | Plán ve vyvojovy_plan.md, ale žádný kód (ani backend ani frontend) |
| **Image zoom modals** | Částečně | `openImageModal()` referencováno ale ne plně definováno |
| **Schema editor** | Částečně | Schéma se načítá ale nemá edit UI |
| **Translation Editor** | Funguje jen online | Vyžaduje HLINÍK backend (`/api/translations/`) |

### Mrtvý kód / nesrovnalosti

- README zmiňuje D3.js, ale graf používá vlastní canvas implementaci (graph.js)
- Fallback data v app.js pro testy jsou zastaralá
- config.json odkazuje na `legacy/roles.json` a `legacy/relations.json` — adresář legacy neexistuje
- `index.html.bak` — záložní kopie (62KB), zbytečná v repu

### Velikost souborů

- app.js: 186KB (4662 řádků) — velký monolitický soubor
- index.html: 146KB — veškerý HTML v jednom souboru
- style.css: 62KB
- assets/images: ~30MB (44 PNG souborů)

---

## Integrace s HLINÍK

### Lore Editor API (`/api/lore-editor/`)
- Plně funkční CRUD — files, records, schema, references
- Auth přes Bearer token z localStorage
- Graceful degradace: když server neběží, editor zobrazí "Read-only"

### Translation API (`/api/translations/`)
- Načítání a editace překladových souborů
- Funguje jen když HLINÍK běží

### Plánované: Generators API (`/api/generators/`)
- Neexistuje ani v HLINÍK backendu ani ve frontend kódu

---

## Data

| Soubor | Záznamy | Popis |
|--------|---------|-------|
| users.json | 20 | 8 Users + 8 Agents + 4 Admins |
| relations_v2.json | 14 | Vztahy mezi postavami |
| tasks.json | 60 | Herní úkoly |
| abilities.json | 20 | Schopnosti postav |
| story_nodes.json | 16 | Příběhové uzly |
| features.json | 240 | HLINÍK features se stavy |
| timeline.json | 18+ | Události v 6 fázích |
| roles.json | 4 | Definice rolí |
| llm_prompts.json | 4 | Systémové prompty |
| relation_types.json | 14 | Typy vztahů |
| task_types.json | ~6 | Typy úkolů |
| players/ | 17 souborů | Individuální profily (U01-U08, A01-A08, S01-S04) |
| test_runs/ | 130 souborů | Historie testů |
