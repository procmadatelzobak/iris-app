# IRIS Translation System - Dokumentační Index

## 📚 Návod k dokumentaci

Tento adresář obsahuje kompletní překladový systém pro IRIS aplikaci. Zde je průvodce, jak číst dokumentaci podle vašich potřeb.

---

## 🎯 Vyberte si podle vašeho cíle:

### "Chci rychle začít s implementací"
👉 **Začněte s:** [`QUICKSTART.md`](./QUICKSTART.md)
- 5-minutový start s testováním
- 30-minutová minimální implementace
- Okamžitě spustitelné příklady

---

### "Chci pochopit, jak systém funguje"
👉 **Začněte s:** [`README.md`](./README.md)
- Přehled systému
- Struktura souborů
- Priorita načítání
- Architektura

👉 **Pak pokračujte:** [`SUMMARY.md`](./SUMMARY.md)
- Kompletní souhrn toho, co bylo vytvořeno
- Statistiky (212 překladů, 38 overrides)
- Stav implementace
- Kontrolní seznamy

---

### "Chci implementovat kompletní systém"
👉 **Postupujte podle:** [`INTEGRATION_GUIDE.md`](./INTEGRATION_GUIDE.md)
- Fáze 1: Backend integrace (DB, API)
- Fáze 2: Frontend integrace (JS, WebSocket)
- Fáze 3: HTML template updates
- Fáze 4: Root dashboard UI
- Fáze 5: Testing
- Fáze 6: Deployment

**Odhadovaný čas:** 6-8 hodin

---

### "Chci vidět konkrétní příklady použití"
👉 **Prohlédněte si:** [`EXAMPLE_USAGE.md`](./EXAMPLE_USAGE.md)
- 10 reálných scénářů
- Code examples pro každý scénář
- Ukázky Backend + Frontend kódu
- Testing checklist

---

## 📁 Přehled všech souborů

### Produkční soubory (použité v aplikaci)

| Soubor | Účel | Velikost | Status |
|--------|------|----------|--------|
| `czech.json` | České překlady pro celé UI | 219 klíčů | ✅ Ready |
| `english.json` | Anglické překlady pro celé UI | 219 klíčů | ✅ Ready |
| `crazy.json` | Crazy Czech překlady (LARP efekt) | 219 klíčů | ✅ Ready |
| `iris.json` | LARP admin terminologie | 38 klíčů | ✅ Ready |
| `__init__.py` | Python loading modul | ~4KB | ✅ Functional |
| `test_translations.py` | Automatizované testy | ~6KB | ✅ Passing |

### Dokumentační soubory

| Soubor | Účel | Pro koho | Čas čtení |
|--------|------|----------|-----------|
| `README.md` | Přehled systému | Všichni | 5 min |
| `QUICKSTART.md` | Rychlý start | Vývojáři | 5 min |
| `INTEGRATION_GUIDE.md` | Kompletní implementace | Vývojáři | 20 min |
| `EXAMPLE_USAGE.md` | Konkrétní příklady | Vývojáři | 15 min |
| `SUMMARY.md` | Souhrn a statistiky | Management | 10 min |
| `INDEX.md` | Tento soubor | Všichni | 2 min |

---

## 🚦 Rychlá orientace - Kde najdu co?

### Potřebuji přidat nový překlad
📄 **Editujte:** `czech.json`  
📖 **Návod:** `README.md` sekce "Strukturace klíčů"

### Potřebuji změnit IRIS terminologii
📄 **Editujte:** `iris.json`  
📖 **Návod:** `README.md` sekce "iris.json"

### Potřebuji použít překlad v Python kódu
📄 **Import z:** `__init__.py`  
📖 **Příklad:** `EXAMPLE_USAGE.md` Scénář 1

### Potřebuji použít překlad v JavaScript
📄 **Vytvořit:** `static/js/translations.js`  
📖 **Návod:** `INTEGRATION_GUIDE.md` sekce 2.1

### Potřebuji otestovat systém
📄 **Spustit:** `test_translations.py`  
📖 **Návod:** `QUICKSTART.md` sekce 2

### Potřebuji implementovat custom labels
📖 **Návod:** `INTEGRATION_GUIDE.md` sekce 1.1  
📝 **Příklad:** `EXAMPLE_USAGE.md` Scénář 3

### Potřebuji real-time updates
📖 **Návod:** `INTEGRATION_GUIDE.md` sekce 2.2  
📝 **Příklad:** `EXAMPLE_USAGE.md` Scénář 4

---

## 🎓 Učební cesta (doporučené pořadí)

### Den 1: Pochopení systému (1 hodina)
1. ✅ Přečíst `README.md` (5 min)
2. ✅ Prohlédnout `czech.json` a `iris.json` (10 min)
3. ✅ Spustit `test_translations.py` (5 min)
4. ✅ Vyzkoušet v Python REPL (10 min) - viz `QUICKSTART.md`
5. ✅ Přečíst `SUMMARY.md` (10 min)
6. ✅ Prohlédnout `EXAMPLE_USAGE.md` scénáře 1-3 (20 min)

### Den 2: Minimální implementace (3 hodiny)
1. ✅ Následovat `QUICKSTART.md` Fáze 1 (30 min)
2. ✅ Následovat `QUICKSTART.md` Fáze 2 (30 min)
3. ✅ Následovat `QUICKSTART.md` Fáze 3 (30 min)
4. ✅ Otestovat v browseru (30 min)
5. ✅ Studovat `INTEGRATION_GUIDE.md` Fáze 1-2 (60 min)

### Den 3-4: Kompletní implementace (4-6 hodin)
1. ✅ Implementovat DB layer (2 hod) - `INTEGRATION_GUIDE.md` Fáze 1
2. ✅ Implementovat frontend (2 hod) - `INTEGRATION_GUIDE.md` Fáze 2-3
3. ✅ Implementovat UI (1 hod) - `INTEGRATION_GUIDE.md` Fáze 4
4. ✅ Testing (1 hod) - `INTEGRATION_GUIDE.md` Fáze 5

---

## 🔍 Hledání konkrétních informací

### Technické detaily
- **Priorita načítání:** `README.md` sekce "Priorita načítání"
- **Strukturace klíčů:** `README.md` sekce "Strukturace klíčů"
- **Python API:** `__init__.py` docstringy funkcí
- **WebSocket flow:** `INTEGRATION_GUIDE.md` sekce 2.2

### Code examples
- **Backend příklady:** `EXAMPLE_USAGE.md` sekce Backend v každém scénáři
- **Frontend příklady:** `EXAMPLE_USAGE.md` sekce Frontend v každém scénáři
- **Test příklady:** `test_translations.py` všechny test funkce

### Troubleshooting
- **Backend problémy:** `INTEGRATION_GUIDE.md` sekce "Troubleshooting"
- **Frontend problémy:** `QUICKSTART.md` sekce "Troubleshooting"
- **Test problémy:** `test_translations.py` dokumentace funkcí

---

## 📊 Stav projektu

### Co je hotové ✅
- Translation files (czech.json, iris.json)
- Python loading module
- Kompletní dokumentace (6 souborů)
- Test suite (100% passing)
- Integration guide
- Usage examples
- Quick start guide

### Co čeká na implementaci ⏳
- Database migrace
- API endpoints
- Frontend TranslationManager
- WebSocket handlers
- UI integration

### Odhadovaný čas do produkce
**6-8 hodin** aktivního vývoje podle `INTEGRATION_GUIDE.md`

---

## 💡 Tipy pro efektivní práci

1. **Začněte s QUICKSTART.md** - získáte fungující prototyp za 30 minut
2. **Následujte INTEGRATION_GUIDE.md postupně** - každá fáze je testovatelná samostatně
3. **Používejte EXAMPLE_USAGE.md jako referenci** - obsahuje řešení běžných problémů
4. **Spouštějte testy pravidelně** - `test_translations.py` vás upozorní na chyby
5. **Studujte README.md důkladně** - obsahuje důležité koncepty (priority, fallbacks)

---

## 📞 Podpora

### Máte otázku o systému?
→ Pravděpodobně odpověď najdete v `README.md`

### Chcete implementovat konkrétní feature?
→ Hledejte v `EXAMPLE_USAGE.md` podobný scénář

### Nevíte, jak začít?
→ Následujte `QUICKSTART.md` krok za krokem

### Potřebujete detailní návod?
→ `INTEGRATION_GUIDE.md` má 6 fází s code examples

### Chcete vědět, co všechno systém umí?
→ `SUMMARY.md` má kompletní přehled

---

## 🎯 Pro různé role

### Pro Backend vývojáře
**Start:** `INTEGRATION_GUIDE.md` Fáze 1  
**Reference:** `__init__.py` + `EXAMPLE_USAGE.md` Backend části

### Pro Frontend vývojáře
**Start:** `INTEGRATION_GUIDE.md` Fáze 2  
**Reference:** `EXAMPLE_USAGE.md` Frontend části

### Pro Fullstack vývojáře
**Start:** `QUICKSTART.md` → `INTEGRATION_GUIDE.md`  
**Reference:** `EXAMPLE_USAGE.md` celé scénáře

### Pro Project Managery
**Čtěte:** `SUMMARY.md` + tento `INDEX.md`  
**Focus:** Sekce "Stav implementace" a časové odhady

### Pro QA/Testery
**Spusťte:** `test_translations.py`  
**Čtěte:** `INTEGRATION_GUIDE.md` Fáze 5 (Testing)

---

**Poslední update:** 2025-12-15  
**Verze dokumentace:** 1.1.0 (Phase 37)  
**Status:** ✅ Complete & Ready

---

## ⭐ Quick Links

- 🚀 [Quick Start](./QUICKSTART.md) - Začněte zde
- 📖 [README](./README.md) - Pochopte systém
- 🔧 [Integration Guide](./INTEGRATION_GUIDE.md) - Implementujte systém
- 💡 [Examples](./EXAMPLE_USAGE.md) - Vidějte příklady
- 📊 [Summary](./SUMMARY.md) - Zjistěte celkový stav
