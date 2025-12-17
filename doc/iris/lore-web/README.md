# IRIS Organizátorská Wiki (Lore-Web)

**Verze:** 4.2.0 | **Phase:** 38 | **Aktualizace:** 2025-12-16

## 📋 O projektu

Lore-Web je dokumentační a organizátorská wiki pro LARP projekt IRIS/HLINÍK. Obsahuje:

- **20 postav** s detailními popisy, cíli a schopnostmi
- **14 vztahů** mezi postavami
- **Příručky** pro hráče (Users, Agents, Admins, Root)
- **Timeline** událostí během hry
- **Features** aplikace HLINÍK
- **Testovací výsledky** a protokoly

---

## 🚀 Spuštění (Offline)

Web funguje **zcela offline** bez potřeby serveru:

```bash
# Linux/macOS - otevřít v prohlížeči
xdg-open doc/iris/lore-web/index.html
# nebo
open doc/iris/lore-web/index.html

# Windows
start doc\iris\lore-web\index.html
```

Nebo jednoduše otevřete `index.html` přímo ve vašem prohlížeči.

### ⚠️ CORS omezení

Kvůli bezpečnostním omezením prohlížečů při `file://` protokolu některé funkce (jako dynamické načítání JSON) používají fallback data zabudovaná přímo v JavaScriptu.

---

## 📁 Struktura dat

```
data/
├── meta.json           # Verze, fáze, metadata webu
├── config.json         # Základní konfigurace
│
├── players/            # Informace o postavách
│   ├── index.json      # Seznam všech 20 postav
│   ├── U01.json        # Uživatelé (U01-U08)
│   ├── A01.json        # Agenti (A01-A08)
│   └── S01.json        # Správci/Admini (S01-S04)
│
├── relations/          # Vztahy mezi postavami
│   └── index.json      # 14 vztahů s popisy
│
├── lore/               # Příběhové informace
│   ├── timeline.json   # 18 událostí ve 6 fázích
│   └── definitions.json # Definice systému
│
├── manuals/            # Příručky
│   ├── index.json      # Seznam manuálů
│   ├── user.html       # Příručka pro uživatele
│   ├── agent.html      # Příručka pro agenty
│   ├── admin.html      # Příručka pro správce
│   └── root.html       # Příručka pro ROOT
│
├── hlinik/             # Data aplikace HLINÍK
│   ├── features.json   # 240 features
│   ├── llm_prompts.json # LLM prompty
│   └── issues.json     # Úkoly/Issues
│
└── tests/              # Testovací data
    ├── scenarios.json  # Testovací scénáře
    ├── protocols/      # Protokoly testů
    └── runs/           # Výsledky běhů
```

---

## 📝 Editace obsahu

### Úprava postavy

Každá postava je v samostatném souboru `data/players/{ID}.json`:

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

### Přidání nového vztahu

Editujte `data/relations/index.json`:

```json
{
    "source": "U01",
    "target": "A01", 
    "type": "past",
    "desc_source": "Co ví source o target",
    "desc_target": "Co ví target o source"
}
```

Typy vztahů: `past`, `trade`, `blackmail`, `romance`, `plot`, `empathy`, `rival`, `investigation`, `alliance`, `affection`, `ambition`, `conflict`, `care`, `suspicion`

---

## 🖼️ Obrázky

Avatary a pracovní obrázky jsou v `assets/images/`:

- `avatar_{ID}.png` - Portréty postav
- `work_{ID}.png` - Pracovní prostředí
- `infographic_*.png` - Informační grafiky

---

## 🔧 Technologie

- **HTML5** - Struktura
- **CSS3** - Styly (Glassmorphism, Dark theme)
- **Vanilla JavaScript** - Logika (`app.js`, `js/graph.js`)
- **D3.js** - Vizualizace grafu vztahů
- **JSON** - Datové úložiště

---

## 📞 Kontakt

- **Projekt:** IRIS LARP
- **Verze:** HLINÍK Phase 38
- **Repository:** `iris-app/doc/iris/lore-web/`

---

*Dokumentace je součástí projektu IRIS - Integrovaný Responzivní Inteligentní Systém*
