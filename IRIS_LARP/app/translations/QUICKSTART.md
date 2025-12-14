# Quick Start Guide - IRIS Translation System

## Pro koho je tento průvodce

Tento průvodce je pro vývojáře, který chce **okamžitě začít** implementovat překladový systém do IRIS aplikace.

---

## ⚡ 5-minutový start

### 1. Zkontrolujte, že soubory existují

```bash
ls IRIS_LARP/app/translations/
# Měli byste vidět:
# - czech.json
# - iris.json
# - __init__.py
# - README.md (a další dokumentaci)
```

### 2. Spusťte testy

```bash
cd IRIS_LARP/app/translations
python3 test_translations.py
```

**Očekávaný výstup:**
```
✓ All tests completed!
```

### 3. Vyzkoušejte translation modul v Python REPL

```python
from IRIS_LARP.app.translations import get_translation, load_translations

# Načíst české překlady
czech = load_translations("czech")
print(czech["login"]["username_label"])  # "IDENTIFIKÁTOR"

# Získat překlad pomocí funkce
text = get_translation("login.password_label", "cz")
print(text)  # "HESLO"

# Vyzkoušet IRIS režim
text = get_translation("admin_dashboard.hub_station_1", "czech-iris")
print(text)  # "UMYVADLO"

# Vyzkoušet custom override
custom = {"login.username_label": "MŮJ CUSTOM TEXT"}
text = get_translation("login.username_label", "cz", custom)
print(text)  # "MŮJ CUSTOM TEXT"
```

---

## 🚀 První implementace (30 minut)

### Fáze 1: Backend minimální implementace

#### A) Vytvořit API endpoint pro získání překladů

Vytvořte soubor `IRIS_LARP/app/routers/translations.py`:

```python
from fastapi import APIRouter, Depends
from app.translations import load_translations
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/translations", tags=["translations"])

@router.get("/")
async def get_translations(user = Depends(get_current_user)):
    """Vrátí všechny překlady pro Czech jazyk."""
    return {
        "language_mode": "cz",
        "translations": load_translations("czech"),
        "custom_labels": {}  # Zatím prázdné, později z DB
    }
```

#### B) Zaregistrovat router v main.py

```python
# V main.py
from app.routers import translations

app.include_router(translations.router)
```

#### C) Test endpoint

```bash
# Spusťte server
python run.py

# V jiném terminálu
curl http://localhost:8000/api/translations/
# Měli byste vidět JSON s translations
```

---

### Fáze 2: Frontend minimální implementace

#### A) Vytvořit TranslationManager

Vytvořte soubor `IRIS_LARP/static/js/translations.js`:

```javascript
class TranslationManager {
    constructor() {
        this.translations = {};
        this.languageMode = 'cz';
    }

    async init() {
        try {
            const response = await fetch('/api/translations/');
            const data = await response.json();
            
            this.translations = data.translations;
            this.languageMode = data.language_mode;
            
            console.log('✓ Translations loaded:', Object.keys(this.translations));
        } catch (err) {
            console.error('Failed to load translations:', err);
        }
    }

    get(keyPath) {
        const keys = keyPath.split('.');
        let value = this.translations;
        
        for (const key of keys) {
            if (!value || typeof value !== 'object') return keyPath;
            value = value[key];
        }
        
        return value || keyPath;
    }
}

window.translationManager = new TranslationManager();

document.addEventListener('DOMContentLoaded', () => {
    window.translationManager.init();
});
```

#### B) Přidat script do base.html

```html
<!-- V base.html před closing </body> -->
<script src="/static/js/translations.js"></script>
```

#### C) Test v browser console

```javascript
// Otevřete browser console (F12)
window.translationManager.get('login.username_label')
// Mělo by vrátit: "IDENTIFIKÁTOR"
```

---

### Fáze 3: První vizuální integrace

#### Testovací stránka

Vytvořte `IRIS_LARP/app/templates/test_translations.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Translation Test</title>
</head>
<body>
    <h1>Translation System Test</h1>
    
    <div id="results">
        <p>Loading translations...</p>
    </div>

    <script src="/static/js/translations.js"></script>
    <script>
        async function testTranslations() {
            await window.translationManager.init();
            
            const tests = [
                'login.username_label',
                'login.password_label',
                'user_terminal.logout',
                'admin_dashboard.hub_station_1'
            ];
            
            const results = document.getElementById('results');
            results.innerHTML = '<h2>Results:</h2>';
            
            tests.forEach(key => {
                const value = window.translationManager.get(key);
                results.innerHTML += `<p><strong>${key}:</strong> ${value}</p>`;
            });
        }
        
        document.addEventListener('DOMContentLoaded', testTranslations);
    </script>
</body>
</html>
```

#### Přidat route v main.py

```python
from fastapi.responses import HTMLResponse

@app.get("/test-translations", response_class=HTMLResponse)
async def test_translations():
    with open("IRIS_LARP/app/templates/test_translations.html") as f:
        return f.read()
```

#### Otevřít v browseru

```
http://localhost:8000/test-translations
```

Měli byste vidět 4 překlady zobrazené na stránce.

---

## 📋 Kontrolní seznam - Co funguje?

Po těchto 3 fázích byste měli mít:

- [x] Translation soubory načtené
- [x] API endpoint vrací překlady
- [x] Frontend TranslationManager funguje
- [x] Překlady zobrazitelné v browser console
- [x] Test stránka zobrazuje překlady

---

## 🎯 Co dál? (Podle priority)

### Option A: Pokračovat s editací (Pro admin panel)

**Další krok:** Implementovat UI pro "PŘEPSAT REALITU"
- Přidat edit mode toggle button
- Umožnit kliknutí na texty s `data-key`
- Zobrazit prompt/modal pro editaci
- Uložit do localStorage (zatím, později DB)

**Čas:** ~1 hodina

**Návod:** Viz `INTEGRATION_GUIDE.md` sekce "2.3 Edit Mode UI"

---

### Option B: Pokračovat s DB persistencí (Pro produkci)

**Další krok:** Přidat CustomLabel do databáze
- Vytvořit DB model
- Vytvořit migrace
- API endpointy pro save/delete
- Načítat custom labels z DB

**Čas:** ~2 hodiny

**Návod:** Viz `INTEGRATION_GUIDE.md` sekce "1.1 Přidání Custom Labels do Databáze"

---

### Option C: Pokračovat s real-time updates (Pro multi-user)

**Další krok:** WebSocket broadcast
- Handler pro translation_update messages
- Broadcast při změně custom labelu
- Frontend listener pro updates

**Čas:** ~1 hodina

**Návod:** Viz `INTEGRATION_GUIDE.md` sekce "2.2 WebSocket Updates"

---

## 🆘 Troubleshooting

### "Module not found" error v Pythonu

**Problém:** `ImportError: No module named 'app.translations'`

**Řešení:**
```bash
# Ujistěte se, že jste v root directory
cd /path/to/iris-app/IRIS_LARP

# Spusťte Python s PYTHONPATH
PYTHONPATH=. python
>>> from app.translations import get_translation
```

---

### "Failed to load translations" v browseru

**Problém:** Console error při načítání `/api/translations/`

**Řešení:**
1. Ověřte, že server běží: `curl http://localhost:8000/api/translations/`
2. Zkontrolujte, že router je zaregistrován v main.py
3. Zkontrolujte network tab v browser devtools

---

### Překlady se nenačítají z JSON

**Problém:** `get_translation()` vrací klíč místo překladu

**Řešení:**
```python
# Zkontrolujte, že soubory existují
import os
print(os.path.exists("IRIS_LARP/app/translations/czech.json"))

# Zkuste načíst manuálně
import json
with open("IRIS_LARP/app/translations/czech.json") as f:
    data = json.load(f)
    print(data["login"]["username_label"])
```

---

## 📚 Další zdroje

- **Kompletní implementace:** `INTEGRATION_GUIDE.md`
- **Příklady použití:** `EXAMPLE_USAGE.md`
- **Přehled systému:** `README.md`
- **Souhrn:** `SUMMARY.md`

---

## 💬 Máte otázky?

1. Přečtěte si `README.md` pro pochopení systému
2. Prohlédněte `EXAMPLE_USAGE.md` pro konkrétní scénáře
3. Následujte `INTEGRATION_GUIDE.md` pro krok-za-krokem návod

---

**Status:** 🚀 Ready to implement  
**Odhadovaný čas na kompletní implementaci:** 6-8 hodin  
**Důležité:** Začněte s minimální implementací (tento quickstart), pak postupně přidávejte features.
