# Lore-Web — Audit stavu aplikace

**Datum:** 2026-03-14 (aktualizováno)

## Celkový stav

Aplikace je **funkční a stabilní**. Většina featur funguje, offline režim spolehlivý.

---

## Co funguje

- Dashboard se statistikami
- Role definitions (4 role s detailními popisy)
- Users/Players grid s avatary a briefings
- Interaktivní graf vztahů (canvas, vlastní fyzika, 14 typů vztahů)
- Seznam vztahů s filtrováním
- Timeline (6 fází)
- Feature tabulka (240 HLINÍK featur s filtrováním)
- LLM Prompts zobrazení + kopírování
- PDF export (jednotlivé briefings, bulk ZIP, manuály)
- Test viewer (historie testů)
- JSON Editor / Lore Editor (plný CRUD přes HLINÍK API)
- Offline režim (fallback na embedded data)
- Print support

---

## Opraveno (2026-03-14)

- ~~Nekonzistentní verze v UI~~ — odstraněny hardcoded verze z titulků
- ~~Legacy cesty v config.json~~ — odstraněny
- ~~index.html.bak~~ — smazán
- ~~D3.js reference v README~~ — opravena (graf používá vlastní canvas)

---

## Zbývající problémy

| Feature | Stav | Poznámka |
|---------|------|----------|
| **Generators modul** | Neimplementováno | Plán ve vyvojovy_plan.md |
| **Image zoom modals** | Částečně | `openImageModal()` referencováno ale ne plně definováno |
| **Translation Editor** | Jen online | Vyžaduje HLINÍK backend |

### Velikost souborů

- app.js: 186KB (4662 řádků) — monolitický, ale funkční
- index.html: 143KB — veškerý HTML v jednom souboru
- assets/images: ~30MB (44 PNG souborů)

---

## Data

| Soubor | Záznamy | Popis |
|--------|---------|-------|
| users.json | 20 | 8 Users + 8 Agents + 4 Admins |
| relations_v2.json | 14 | Vztahy mezi postavami |
| tasks.json | 10 | Herní úkoly se stopami k Eltexu |
| story_nodes.json | 10 | Klíčové příběhové uzly |
| timeline.json | 6 | Události v 6 herních fázích |
| players/ | 21 souborů | Individuální profily + index |
| features.json | 240 | HLINÍK features se stavy |
| roles.json | 4 | Definice rolí |
| llm_prompts.json | 4 | Systémové prompty |
| relation_types.json | 14 | Typy vztahů |
