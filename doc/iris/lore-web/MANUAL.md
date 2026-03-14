# Lore-Web — Kompletní návod

**Verze:** 4.2.0 | **Phase:** 38 | **Datum:** 2026-03-14

Tento dokument je **závazná specifikace** aplikace Lore-Web. Kód musí odpovídat tomuto návodu.

---

## 1. Přehled

Lore-Web je organizátorská wiki a plánovací nástroj pro LARP projekt IRIS. Je to **klientská SPA** (Single Page Application) — vanilla JS + HTML + CSS, žádný framework. Data jsou v JSON souborech.

### 1.1 Dva režimy provozu

| Režim | Jak spustit | Funkce |
|-------|-------------|--------|
| **Offline** | Otevřít `index.html` přímo v prohlížeči | Vše funguje kromě editoru a překladů. Data se čtou z JSON souborů. |
| **Online** | Přes HLINÍK server na `/lore-web` | Vše funguje + Lore Editor (CRUD) + Translation Editor. Vyžaduje auth token. |

### 1.2 Struktura souborů

```
lore-web/
├── index.html          # Celá SPA (HTML)
├── app.js              # Veškerá logika (JS)
├── style.css           # Styly
├── js/graph.js         # Interaktivní graf vztahů (canvas)
├── templates/          # HTML šablony pro briefings a tooltipy
├── assets/images/      # Avatary, pracovní fotky, infografiky
└── data/               # Veškerá herní data (JSON)
    ├── meta.json       # Verze, metadata
    ├── config.json     # Konfigurace, cesty k souborům
    ├── users.json      # 20 postav
    ├── roles.json      # 4 definice rolí
    ├── relations_v2.json # 14 vztahů
    ├── tasks.json      # 60 úkolů
    ├── abilities.json  # 20 schopností
    ├── story_nodes.json # 16 příběhových uzlů
    ├── timeline.json   # Události v 6 fázích
    ├── features.json   # 240 HLINÍK featur
    ├── llm_prompts.json # 4 systémové prompty
    ├── relation_types.json # 14 typů vztahů
    ├── task_types.json # Typy úkolů
    ├── players/        # Individuální profily (U01.json, A01.json, S01.json...)
    ├── relations/      # index.json
    ├── lore/           # definitions.json, timeline.json
    ├── manuals/        # HTML manuály (user, agent, admin, root)
    ├── hlinik/         # features, issues, llm_prompts
    ├── test_runs/      # Historie testů
    └── tests/          # Testovací scénáře
```

---

## 2. Navigace

SPA má 5 hlavních kategorií v menu:

### 2.1 Dashboard
Výchozí stránka. Zobrazuje:
- Statistiky: počty postav (8 Users, 8 Agents, 4 Admins), počet vztahů
- Verze systému
- Rychlé odkazy na klíčové sekce

### 2.2 Lore

| Sekce | Obsah |
|-------|-------|
| **Role** | 4 definice rolí (User, Agent, Admin, Root) s detailními popisy |
| **Uživatelé** | Grid 20 postav s avatary. Klik = briefing modal |
| **Vztahy** | Interaktivní graf + seznam. Filtrování podle postavy |
| **Manuály** | Herní příručky (user, agent, admin, root) |
| **Příběh** | Story nodes — příběhové uzly s vazbami |
| **Hráči** | Detailní karty hráčů s pracovními fotkami |
| **Prompty** | 4 LLM systémové prompty (task, hyper, optimizer, censor) |
| **Timeline** | Události organizované po fázích (6 fází) |
| **Jazyky** | Editor překladů (vyžaduje HLINÍK backend) |

### 2.3 HLINÍK

| Sekce | Obsah |
|-------|-------|
| **Dokumentace** | API dokumentace HLINÍK |
| **Systém** | Popis systémových komponent |
| **Konfigurace** | Herní nastavení |
| **Testy** | Historie testovacích běhů s logy |
| **LLM Prompty** | Systémové prompty (kopie z Lore) |
| **Vizualizace** | Grafová vizualizace |

### 2.4 Správa

| Sekce | Obsah |
|-------|-------|
| **Úkoly** | Issue tracker (localStorage persistence) |
| **Testy** | Testovací scénáře a protokoly |
| **Definice** | Systémové definice z JSON |
| **JSON Editor** | Lore Editor — plný CRUD přes HLINÍK API |

### 2.5 O Iris

| Sekce | Obsah |
|-------|-------|
| **Dokumentace** | Dokumentace Lore-Web samotné |
| **Audit** | Compliance report (kód vs design) |
| **Exporty** | PDF/ZIP export dat |

---

## 3. Postavy (Users)

### 3.1 Datový model

Každá postava je v `data/players/{ID}.json`:

```json
{
    "id": "U01",
    "type": "user",
    "name": "Jana Nováková",
    "archetype": "Zadlužená učitelka",
    "description": "Popis postavy...",
    "ability": "Grammar Nazi: ...",
    "goals": ["Cíl 1", "Cíl 2", "Cíl 3"],
    "avatar": "avatar_U01.png",
    "work_image": "work_U01.png",
    "appearance": {
        "gender": "žena",
        "age_range": "45-55",
        "hair_color": "šedivějící hnědé vlasy",
        "face_description": "unavená tvář...",
        "distinctive_features": "..."
    }
}
```

### 3.2 ID konvence

| Prefix | Role | Rozsah |
|--------|------|--------|
| U | User (Subjekt) | U01–U08 |
| A | Agent (Operátor) | A01–A08 |
| S | Admin (Správce) | S01–S04 |

### 3.3 Souhrnný soubor

`data/users.json` obsahuje pole všech 20 postav se základními údaji (id, type, obcanske_jmeno, archetype, kratky_popis).

### 3.4 UI zobrazení

- **Grid**: Avatary v mřížce, klik otevře briefing modal
- **Briefing modal**: Plný profil — avatar, archetyp, schopnost, cíle, vztahy, vzhled
- **Player karty**: Pracovní fotky, detaily, export do PDF

---

## 4. Vztahy (Relations)

### 4.1 Datový model

`data/relations_v2.json`:

```json
{
    "id": "R01",
    "source": "U01",
    "target": "A01",
    "type": "past",
    "desc_source": "Co ví source o target",
    "desc_target": "Co ví target o source"
}
```

### 4.2 Typy vztahů (14)

| Typ | Barva | Popis |
|-----|-------|-------|
| past | fialová | Společná minulost |
| trade | zelená | Obchodní vztah |
| blackmail | červená | Vydírání |
| romance | růžová | Romantický vztah |
| plot | oranžová | Společné spiknutí |
| empathy | světle modrá | Empatie/pochopení |
| rival | tmavě červená | Rivalita |
| investigation | cyan | Vyšetřování |
| alliance | zlatá | Aliance |
| affection | světle růžová | Náklonnost |
| ambition | jantarová | Společné ambice |
| conflict | červená | Konflikt |
| care | zelená | Péče |
| suspicion | šedá | Podezření |

### 4.3 Interaktivní graf

`js/graph.js` — canvas-based vizualizace:
- Force-directed layout (vlastní fyzikální engine, ne D3)
- 3 zóny: Agents (vlevo dole), Admins (nahoře), Users (vpravo dole)
- Interakce: hover (tooltip), drag, filtrování podle hráče
- Barvy uzlů podle role, barvy hran podle typu vztahu

---

## 5. Úkoly (Tasks)

`data/tasks.json` — 60 herních úkolů:

```json
{
    "id": "T01",
    "nazev": "Název úkolu",
    "popis": "Detailní popis...",
    "typ": "TT01",
    "prirazeni": ["U01", "A03"],
    "obtiznost": "medium"
}
```

Typy úkolů definovány v `data/task_types.json`.

---

## 6. Timeline

`data/timeline.json` — události organizované po fázích:

```json
{
    "id": "EVT01",
    "phase": 1,
    "title": "Název události",
    "description": "Co se stalo...",
    "actors": ["U01", "A03"],
    "targets": ["S01"],
    "timestamp": "den 1, ráno"
}
```

6 fází s barevným kódováním. Klik na událost otevře detail modal.

---

## 7. HLINÍK Features

`data/hlinik/features.json` — 240 featur aplikace HLINÍK:

```json
{
    "id": "F001",
    "name": "Název featury",
    "category": "auth",
    "role": "user",
    "status": "DONE",
    "test_status": "tested",
    "description": "Popis..."
}
```

**Stavy:** DONE, PARTIAL, IN_PROGRESS, TODO
**Filtrování:** podle role (User, Agent, Admin, Root) a statusu

---

## 8. LLM Prompty

`data/llm_prompts.json` — 4 systémové prompty pro HLINÍK AI:

| Role | Účel |
|------|------|
| task | Hodnocení úkolů (korporátní tón) |
| hyper | Autopilot odpovědi (empatická AI) |
| optimizer | Přepis do korporátního tónu |
| censor | Sanitizace v panic mode |

UI: zobrazení s kopírováním do clipboardu.

---

## 9. Manuály

`data/manuals/` — HTML příručky pro každou roli:

| Soubor | Pro koho |
|--------|----------|
| user.html | Subjekty |
| agent.html | Agenty |
| admin.html | Správce |
| root.html | ROOT/Gamemaster |
| admin_crazy.html | Crazy verze admin manuálu |

Zobrazují se v modálním okně. Exportovatelné do PDF.

---

## 10. Lore Editor (JSON Editor)

Sekce **Správa > JSON Editor**. Funguje jen s běžícím HLINÍK serverem.

### 10.1 Funkce

- Výběr souboru (users, tasks, relations, abilities, task_types, relation_types, story_nodes, roles, config)
- Seznam záznamů s hledáním
- Formulář pro editaci záznamu (generovaný automaticky ze schématu)
- Vytvoření nového záznamu (auto-generated ID)
- Smazání záznamu (s kontrolou referencí — vrátí 409 pokud existují)
- Detekce typu pole: string, text, integer, number, boolean, reference, array

### 10.2 API

Komunikuje s HLINÍK přes `/api/lore-editor/` endpointy (viz HLINÍK MANUAL.md sekce 10.4).

### 10.3 Autentizace

Bearer token z `localStorage.access_token`. Získá se po přihlášení do HLINÍK.

### 10.4 Offline režim

Když API není dostupné, editor zobrazí "Read-only" a neumožní editaci.

---

## 11. Translation Editor

Sekce **Lore > Jazyky**. Funguje jen s běžícím HLINÍK serverem.

- Načte překladové soubory z `/api/translations/files/list`
- Tabulka klíč-hodnota pro editaci
- Uložení zpět na server přes `/api/translations/files/{code}`

---

## 12. Exporty

Sekce **O Iris > Exporty**:

| Export | Formát | Obsah |
|--------|--------|-------|
| Jednotlivý briefing | PDF (print dialog) | Profil jedné postavy |
| Všechny briefings | ZIP (~3.4 MB) | PDF briefing pro každou z 20 postav |
| Manuály | PDF (print dialog) | Příručka pro vybranou roli |
| Lore-Web data | JSON | Všechna herní data (bez test_runs) |
| Test runs | JSON | Historie testů |

---

## 13. Šablony

`templates/` — HTML šablony s `{{variable}}` substitucí:

| Šablona | Použití |
|---------|---------|
| briefing.html | Briefing modal (profil, vztahy, cíle, vzhled) |
| node_tooltip.html | Tooltip při hoveru nad uzlem grafu |
| relation_tooltip.html | Tooltip při hoveru nad hranou grafu |
| relations_left_panel.html | Sidebar pro filtrování vztahů |

---

## 14. Vizuální design

- **Téma:** Dark glassmorphism (#0a0a0f pozadí, průhledné karty)
- **Akcentní barva:** Zlatá (#d4af37)
- **Role barvy:** User=modrá, Agent=růžová, Admin=zlatá
- **Vztahy:** 14 barev podle typu (viz sekce 4.2)
- **Responsive:** Flexbox/Grid, mobilní navigace
- **Print:** Optimalizované styly pro tisk

---

## 15. Assets

`assets/images/` — 44 PNG souborů (~30 MB):

| Typ | Souborů | Pojmenování | Velikost |
|-----|---------|-------------|----------|
| Avatary | 20 | avatar_{ID}.png | ~630-750 KB |
| Pracovní fotky | 20 | work_{ID}.png | ~630-750 KB |
| Infografiky | 3 | infographic_{topic}.png | ~700-830 KB |
| Ostatní | 1 | panopticon_graph.png | ~515 KB |

---

## 16. Integrace s HLINÍK

Lore-Web je mountována v HLINÍK FastAPI aplikaci na cestě `/lore-web`. Integrace:

| Feature | HLINÍK endpoint | Směr |
|---------|----------------|------|
| Lore Editor | `/api/lore-editor/*` | Lore-Web → HLINÍK (CRUD na JSON data) |
| Translation Editor | `/api/translations/*` | Lore-Web → HLINÍK (editace překladů) |
| Admin Lore View | `/api/admin/lore/data` | HLINÍK → Lore-Web data (roles, relations) |
| ROOT Dashboard | iframe/embed | HLINÍK embeduje Lore-Web |

Lore-Web funguje i samostatně (offline), ale editor funkce vyžadují běžící HLINÍK.

---

## 17. Plánované featury (neimplementováno)

### Generators modul
Plán ve `vyvojovy_plan.md`. Účel: spouštění LLM skriptů pro generování/úpravu herního obsahu.

**Backend (HLINÍK):**
- Nový router `generators_api.py`
- `GET /api/generators/scripts` — seznam skriptů
- `POST /api/generators/run` — spuštění skriptu

**Frontend (Lore-Web):**
- Nová sekce "Generátory" v menu pod Lore
- Wizard UI pro konfiguraci
- Log konzole pro průběh

**První skript:** `update_user_profile` — LLM generuje jméno a popisy podle archetypu.

Stav: 0% implementováno, existuje pouze design dokument.

---

## 18. Známá omezení

1. **Monolitický app.js** — 4662 řádků, 186KB. Refaktoring na moduly by zlepšil údržbu.
2. **Velké obrázky** — 30MB PNG souborů, žádná optimalizace/komprese.
3. **Offline CORS** — při `file://` protokolu některé fetch volání selžou, fallback na embedded data.
4. **Žádná validace** — Lore Editor nevaliduje schéma při ukládání.
5. **localStorage persistence** — Issues/Tasks v sekci Správa se ukládají jen do localStorage, ne na server.
