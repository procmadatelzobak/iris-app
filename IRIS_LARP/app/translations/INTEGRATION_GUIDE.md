# Integration Guide - IRIS Translation System

## Rychlý přehled / Quick Overview

Tento průvodce vysvětluje, jak integrovat překladový systém do existující IRIS aplikace.

This guide explains how to integrate the translation system into the existing IRIS application.

---

## Fáze 1: Backend Integrace

### 1.1 Přidání Custom Labels do Databáze

Vytvořte novou tabulku pro ukládání custom admin labelů:

```python
# V database.py nebo models.py

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

class CustomLabel(Base):
    __tablename__ = "custom_labels"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, index=True)  # např. "admin_dashboard.hub_station_1"
    value = Column(Text)  # Vlastní text správce
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 1.2 Přidání System Settings pro jazyk

Rozšiřte `SystemState` nebo vytvořte novou tabulku:

```python
class SystemSettings(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True)
    language_mode = Column(String(50), default="cz")  # "cz" nebo "czech-iris"
    # ... další settings
```

### 1.3 API Endpointy

Přidejte do `routers/` nový soubor `translations.py`:

```python
from fastapi import APIRouter, Depends
from app.translations import get_translation, load_translations, clear_cache
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/translations", tags=["translations"])

@router.get("/")
async def get_all_translations(user = Depends(get_current_user)):
    """Získat všechny překlady pro aktuální jazyk."""
    # Načíst language_mode z DB
    language_mode = get_system_language_mode()  # Implementujte tuto funkci
    
    # Načíst custom labels z DB
    custom_labels = get_custom_labels_dict()  # Implementujte tuto funkci
    
    # Načíst base translations
    if language_mode == "czech-iris":
        czech = load_translations("czech")
        iris = load_translations("iris")
        from app.translations import merge_translations
        translations = merge_translations(czech, iris)
    else:
        translations = load_translations("czech")
    
    # Sloučit s custom labels
    # ... merge logic
    
    return {
        "language_mode": language_mode,
        "translations": translations,
        "custom_labels": custom_labels
    }

@router.post("/custom-label")
async def set_custom_label(
    key: str, 
    value: str, 
    user = Depends(require_admin)
):
    """Nastavit custom label (pouze admin)."""
    # Uložit do DB
    db_label = CustomLabel(key=key, value=value)
    # ... save logic
    
    # Broadcast změnu přes WebSocket
    await broadcast_translation_update(key, value)
    
    return {"status": "ok", "key": key, "value": value}

@router.delete("/custom-label/{key}")
async def delete_custom_label(
    key: str,
    user = Depends(require_admin)
):
    """Smazat custom label."""
    # Smazat z DB
    # ... delete logic
    
    # Broadcast změnu
    await broadcast_translation_update(key, None)
    
    return {"status": "deleted", "key": key}

@router.post("/reset-all-labels")
async def reset_all_custom_labels(user = Depends(require_admin)):
    """Reset všech custom labelů."""
    # Smazat všechny z DB
    # ... delete all logic
    
    # Broadcast reset
    await broadcast_translation_reset()
    
    return {"status": "reset"}

@router.post("/set-language")
async def set_system_language(
    language_mode: str,  # "cz" nebo "czech-iris"
    user = Depends(require_admin)
):
    """Změnit systémový jazyk (pouze root)."""
    if language_mode not in ["cz", "czech-iris"]:
        return {"error": "Invalid language mode"}
    
    # Uložit do DB
    # ... save logic
    
    # Clear cache
    clear_cache()
    
    # Broadcast změnu
    await broadcast_language_change(language_mode)
    
    return {"status": "ok", "language_mode": language_mode}
```

---

## Fáze 2: Frontend Integrace

### 2.1 JavaScript Translation Manager

Vytvořte nový soubor `/static/js/translations.js`:

```javascript
class TranslationManager {
    constructor() {
        this.translations = {};
        this.customLabels = {};
        this.languageMode = 'cz';
    }

    async init() {
        // Načíst překlady ze serveru
        const response = await fetch('/api/translations/');
        const data = await response.json();
        
        this.translations = data.translations;
        this.customLabels = data.custom_labels;
        this.languageMode = data.language_mode;
        
        // Aktualizovat UI
        this.updateAllLabels();
    }

    get(keyPath) {
        // Priorita: custom labels > language translations
        if (this.customLabels[keyPath]) {
            return this.customLabels[keyPath];
        }
        
        // Navigace nested objektem
        const keys = keyPath.split('.');
        let value = this.translations;
        
        for (const key of keys) {
            if (!value || typeof value !== 'object') return keyPath;
            value = value[key];
        }
        
        return value || keyPath;
    }

    updateAllLabels() {
        // Najít všechny elementy s data-key
        document.querySelectorAll('[data-key]').forEach(el => {
            const key = el.getAttribute('data-key');
            const translation = this.get(key);
            
            // Aktualizovat text (zachovat nested HTML)
            if (el.childNodes.length === 1 && el.childNodes[0].nodeType === Node.TEXT_NODE) {
                el.textContent = translation;
            } else {
                // Pro složitější elementy, aktualizovat pouze text nodes
                this.updateTextNodes(el, translation);
            }
        });
    }

    updateTextNodes(element, newText) {
        // Helper pro aktualizaci pouze textových nodů
        for (let node of element.childNodes) {
            if (node.nodeType === Node.TEXT_NODE) {
                node.textContent = newText;
                break;
            }
        }
    }

    setCustomLabel(key, value) {
        this.customLabels[key] = value;
        
        // Aktualizovat elementy s tímto klíčem
        document.querySelectorAll(`[data-key="${key}"]`).forEach(el => {
            el.textContent = value;
        });
    }

    async saveCustomLabel(key, value) {
        await fetch('/api/translations/custom-label', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ key, value })
        });
        
        this.setCustomLabel(key, value);
    }
}

// Global instance
window.translationManager = new TranslationManager();

// Init on page load
document.addEventListener('DOMContentLoaded', () => {
    window.translationManager.init();
});
```

### 2.2 WebSocket Updates

Do `socket_client.js` přidejte handler:

```javascript
// V handleMessage funkci

if (data.type === 'translation_update') {
    // Real-time aktualizace překladu
    if (window.translationManager) {
        window.translationManager.setCustomLabel(data.key, data.value);
    }
}

if (data.type === 'language_change') {
    // Reload překlady při změně jazyka
    if (window.translationManager) {
        window.translationManager.languageMode = data.language_mode;
        window.translationManager.init();
    }
}

if (data.type === 'translations_reset') {
    // Reset custom labelů
    if (window.translationManager) {
        window.translationManager.customLabels = {};
        window.translationManager.updateAllLabels();
    }
}
```

### 2.3 Edit Mode UI

Do `admin_ui.js` nebo `admin_dashboard.html` přidejte:

```javascript
let editMode = false;

function toggleEditMode() {
    editMode = !editMode;
    
    if (editMode) {
        // Enable editing
        document.querySelectorAll('.editable-label').forEach(el => {
            el.classList.add('editable-active');
            el.style.cursor = 'pointer';
            el.style.border = '1px dashed yellow';
            
            el.addEventListener('click', handleLabelClick);
        });
    } else {
        // Disable editing
        document.querySelectorAll('.editable-label').forEach(el => {
            el.classList.remove('editable-active');
            el.style.cursor = '';
            el.style.border = '';
            
            el.removeEventListener('click', handleLabelClick);
        });
    }
}

function handleLabelClick(e) {
    const element = e.currentTarget;
    const key = element.getAttribute('data-key');
    const currentValue = element.textContent.trim();
    
    const newValue = prompt(`Nový text pro "${key}":`, currentValue);
    
    if (newValue && newValue !== currentValue) {
        window.translationManager.saveCustomLabel(key, newValue);
    }
}
```

---

## Fáze 3: HTML Template Updates

### 3.1 Přidat data-key atributy

Všechny stávající texty, které už mají `editable-label` třídu, už mají `data-key` atributy, takže jsou připravené!

Příklad z `admin/dashboard.html`:
```html
<span class="text-xl font-bold editable-label" data-key="card_sess_${i}">KANÁL ${i}</span>
```

### 3.2 Přidat loading skript

Do `base.html` přidejte:
```html
<script src="/static/js/translations.js"></script>
```

---

## Fáze 4: Root Dashboard UI

### 4.1 Language Selector

Přidejte do root dashboardu sekci pro výběr jazyka:

```html
<!-- V root_dashboard.html -->
<div class="god-panel">
    <div class="god-title">🌍 LANGUAGE SETTINGS</div>
    <div class="space-y-4">
        <div>
            <label class="text-sm text-gray-400">SYSTEM LANGUAGE MODE</label>
            <select id="languageModeSelect" 
                    class="w-full bg-black border border-gray-700 p-2 text-white"
                    onchange="setLanguageMode(this.value)">
                <option value="cz">Czech (Default)</option>
                <option value="czech-iris">Czech + IRIS Admin Terms</option>
            </select>
        </div>
        <div class="text-xs text-gray-500">
            <strong>Czech:</strong> Standardní české překlady<br>
            <strong>Czech + IRIS:</strong> LARP-specifická terminologie pro adminy
        </div>
    </div>
</div>
```

```javascript
async function setLanguageMode(mode) {
    const response = await fetch('/api/translations/set-language', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ language_mode: mode })
    });
    
    if (response.ok) {
        // UI se aktualizuje přes WebSocket broadcast
        showToast('Language mode updated', 'success');
    }
}

// Load current language on page load
async function loadCurrentLanguage() {
    const response = await fetch('/api/translations/');
    const data = await response.json();
    document.getElementById('languageModeSelect').value = data.language_mode;
}
```

---

## Fáze 5: Testing

### 5.1 Unit Tests

```python
# tests/test_translations.py

def test_get_translation_priority():
    """Test že custom labels mají nejvyšší prioritu."""
    custom = {"login.title": "CUSTOM TITLE"}
    result = get_translation("login.title", "cz", custom)
    assert result == "CUSTOM TITLE"

def test_czech_iris_fallback():
    """Test že czech-iris fallbackuje na czech."""
    result = get_translation("common.yes", "czech-iris")
    assert result == "Ano"
```

### 5.2 Integration Tests

1. Změňte jazyk v root dashboardu → ověřte, že se UI aktualizuje
2. Nastavte custom label → ověřte persistenci po reloadu
3. Resetujte custom labels → ověřte, že se vrátí default
4. Otestujte v multi-tab prostředí → ověřte real-time sync

---

## Fáze 6: Deployment

1. Spusťte migrace pro nové DB tabulky
2. Načtěte translation soubory při startu aplikace
3. Nastavte default language_mode v DB
4. Otestujte na staging prostředí

---

## Tipy a Best Practices

1. **Performance**: Cachujte načtené překlady v paměti
2. **Fallbacks**: Vždy vraťte nějaký text (i když je to klíč sám)
3. **Validation**: Validujte custom label inputs (XSS protection)
4. **Backup**: Před resete uložte snapshot custom labelů
5. **Monitoring**: Logujte změny custom labelů pro audit trail

---

## Troubleshooting

**Problém:** Překlady se nenačítají  
**Řešení:** Zkontrolujte konzoli, ověřte že `/api/translations/` vrací data

**Problém:** Custom labels nejsou persistentní  
**Řešení:** Zkontrolujte DB connection, ověřte že API ukládá do DB

**Problém:** Real-time sync nefunguje  
**Řešení:** Zkontrolujte WebSocket connection, ověřte broadcast logic

---

**Autor:** IRIS Development Team  
**Datum:** 2025-12-14  
**Status:** Ready for Implementation
