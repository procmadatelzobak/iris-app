# Příklady použití / Usage Examples

## Ukázkové scénáře pro IRIS Translation System

---

## Scénář 1: Základní použití - Default Czech

**Situace:** Root nezměnil jazyk, používá se default czech.

**Backend:**
```python
from app.translations import get_translation

# Získat překlad pro login screen
username_label = get_translation("login.username_label", "cz")
# Vrátí: "IDENTIFIKÁTOR"

password_label = get_translation("login.password_label", "cz")
# Vrátí: "HESLO"
```

**Frontend:**
```javascript
// V templates
<label data-key="login.username_label">IDENTIFIKÁTOR</label>

// JavaScript automaticky aktualizuje při načtení
window.translationManager.get("login.username_label")
// Vrátí: "IDENTIFIKÁTOR"
```

---

## Scénář 2: IRIS Režim - Admin Terminologie

**Situace:** Root vybral `czech-iris` režim pro LARP-specifickou terminologii.

**Backend:**
```python
# Načtení admin dashboard labels v IRIS režimu
station_name = get_translation("admin_dashboard.hub_station_1", "czech-iris")
# Vrátí: "UMYVADLO" (z iris.json)

station_desc = get_translation("admin_dashboard.hub_desc_1", "czech-iris")
# Vrátí: "MONITORING" (z iris.json)

# Keys které nejsou v iris.json fallbackují na czech.json
logout = get_translation("user_terminal.logout", "czech-iris")
# Vrátí: "ODHLÁSIT" (z czech.json, protože není v iris.json)
```

**Rozdíly mezi režimy:**

| Klíč | `cz` režim | `czech-iris` režim |
|------|-----------|-------------------|
| `admin_dashboard.hub_station_3` | "BAHNO" | "BAHNO" |
| `admin_dashboard.tab_chats` | "ŠUM" | "ŠUM" |
| `admin_dashboard.btn_ai_cfg` | "MODZEK" | "MODZEK" |
| `login.username_label` | "IDENTIFIKÁTOR" | "IDENTIFIKÁTOR" (fallback) |
| `common.yes` | "Ano" | "Ano" (fallback) |

---

## Scénář 3: Custom Admin Override

**Situace:** Admin chce přejmenovat "UMYVADLO" na vlastní název "SANITÁRNÍ MODUL".

**Uživatelský flow:**
1. Admin klikne na tlačítko "PŘEPSAT REALITU"
2. Klikne na text "UMYVADLO"
3. Zadá nový text: "SANITÁRNÍ MODUL"
4. Text se okamžitě změní pro všechny uživatele

**Backend implementace:**
```python
# API endpoint handler
@router.post("/custom-label")
async def set_custom_label(key: str, value: str, user = Depends(require_admin)):
    # 1. Uložit do databáze
    custom_label = CustomLabel(key=key, value=value)
    db.add(custom_label)
    db.commit()
    
    # 2. Broadcast změnu přes WebSocket
    await manager.broadcast({
        "type": "translation_update",
        "key": key,
        "value": value
    })
    
    return {"status": "ok"}
```

**Frontend handlování:**
```javascript
// WebSocket message handler
if (data.type === 'translation_update') {
    window.translationManager.setCustomLabel(data.key, data.value);
    // Všechny elementy s data-key="admin_dashboard.hub_station_1" 
    // se okamžitě aktualizují na "SANITÁRNÍ MODUL"
}
```

**Priority výběru textu:**
```python
# Když admin nastaví custom label
custom_labels = {"admin_dashboard.hub_station_1": "SANITÁRNÍ MODUL"}

# V CZ režimu
text = get_translation("admin_dashboard.hub_station_1", "cz", custom_labels)
# Vrátí: "SANITÁRNÍ MODUL" (custom má přednost)

# V IRIS režimu
text = get_translation("admin_dashboard.hub_station_1", "czech-iris", custom_labels)
# Vrátí: "SANITÁRNÍ MODUL" (custom stále má přednost)
```

---

## Scénář 4: Multi-Session Synchronizace

**Situace:** Admin má otevřené 3 tabs, změní text v jednom.

**Timeline:**
```
T0: Admin v Tab 1 klikne "PŘEPSAT REALITU"
T1: Admin v Tab 1 změní "UMYVADLO" → "REAKTOR A"
T2: Server uloží do DB a broadcastne přes WebSocket
T3: Tab 1, 2, 3 všechny obdrží update message
T4: Všechny taby okamžitě zobrazí "REAKTOR A"
```

**WebSocket broadcast:**
```javascript
// Server pošle všem připojeným klientům
{
    "type": "translation_update",
    "key": "admin_dashboard.hub_station_1",
    "value": "REAKTOR A"
}

// Každý klient aktualizuje lokálně
window.translationManager.setCustomLabel(
    "admin_dashboard.hub_station_1", 
    "REAKTOR A"
);
```

---

## Scénář 5: Reset Custom Labels

**Situace:** Admin chce vrátit všechny texty na výchozí.

**UI Flow:**
1. Admin klikne "AUTO-DESTRUKCE" nebo custom "RESET LABELS" button
2. Potvrdí akci
3. Všechny custom labels se smažou z DB
4. UI se vrátí k default překladům

**Backend:**
```python
@router.post("/reset-all-labels")
async def reset_all_custom_labels(user = Depends(require_admin)):
    # 1. Smazat všechny custom labels z DB
    db.query(CustomLabel).delete()
    db.commit()
    
    # 2. Broadcast reset
    await manager.broadcast({
        "type": "translations_reset"
    })
    
    return {"status": "reset"}
```

**Frontend:**
```javascript
if (data.type === 'translations_reset') {
    // Vyčistit custom labels
    window.translationManager.customLabels = {};
    
    // Reload všechny překlady z server files
    window.translationManager.updateAllLabels();
    
    // "REAKTOR A" se vrátí na "UMYVADLO"
}
```

---

## Scénář 6: Real-time Language Switch

**Situace:** Root přepne jazyk z `cz` na `czech-iris` za běhu.

**Root Dashboard:**
```javascript
async function setLanguageMode(mode) {
    await fetch('/api/translations/set-language', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ language_mode: mode })
    });
    // Server broadcastne změnu
}
```

**Server broadcast:**
```python
@router.post("/set-language")
async def set_system_language(language_mode: str, user = Depends(require_root)):
    # Update DB
    system_settings.language_mode = language_mode
    db.commit()
    
    # Clear translation cache
    clear_cache()
    
    # Broadcast ke všem klientům
    await manager.broadcast({
        "type": "language_change",
        "language_mode": language_mode
    })
```

**Všichni klienti:**
```javascript
if (data.type === 'language_change') {
    window.translationManager.languageMode = data.language_mode;
    
    // Reload překlady (merge czech + iris pokud je czech-iris)
    await window.translationManager.init();
    
    // Celé UI se okamžitě aktualizuje
    // Např. standardní "MONITORING" zůstane, ale admin-specifické 
    // texty se mohou změnit podle iris.json
}
```

---

## Scénář 7: Nested Keys & HTML Elements

**Situace:** Práce se složitějšími elementy s ikonami a nested HTML.

**HTML šablona:**
```html
<!-- Jednoduchý text -->
<span data-key="user_terminal.logout">ODHLÁSIT</span>

<!-- Element s ikonou -->
<button data-key="user_terminal.send_button">
    <i class="fas fa-paper-plane"></i> ODESLAT
</button>

<!-- Složitější struktura -->
<h2 data-key="user_terminal.subject_status">
    <i class="fas fa-id-card"></i> STAV SUBJEKTU
</h2>
```

**Translation Manager handling:**
```javascript
updateAllLabels() {
    document.querySelectorAll('[data-key]').forEach(el => {
        const key = el.getAttribute('data-key');
        const translation = this.get(key);
        
        // Pro elementy s pouze textem
        if (el.childNodes.length === 1 && 
            el.childNodes[0].nodeType === Node.TEXT_NODE) {
            el.textContent = translation;
        } 
        // Pro elementy s nested HTML (ikony atd.)
        else {
            // Najdi a aktualizuj pouze text node
            for (let node of el.childNodes) {
                if (node.nodeType === Node.TEXT_NODE) {
                    node.textContent = translation;
                    break;
                }
            }
        }
    });
}
```

---

## Scénář 8: Dynamic Content (Session Cards)

**Situace:** Generování karet pro 8 sessions s překlady.

**JavaScript šablona:**
```javascript
function initGrid() {
    for (let i = 1; i <= TOTAL_SESSIONS; i++) {
        const card = document.createElement('div');
        
        // Použít translationManager pro dynamic content
        const channelText = window.translationManager.get(`editable_labels.card_sess_${i}`);
        const objectText = window.translationManager.get(`editable_labels.card_user_${i}`);
        const shadowText = window.translationManager.get(`editable_labels.card_agent_${i}`);
        
        card.innerHTML = `
            <span data-key="card_sess_${i}">${channelText}</span>
            <span data-key="card_user_${i}">${objectText}</span>
            <span data-key="card_agent_${i}">${shadowText}</span>
        `;
        
        grid.appendChild(card);
    }
}

// Když admin přejmenuje "KANÁL 3" na "LINKA DELTA"
// WebSocket update automaticky aktualizuje správnou kartu
```

---

## Scénář 9: Fallback & Error Handling

**Situace:** Klíč neexistuje v translation file.

**Backend:**
```python
# Když klíč není v JSON
result = get_translation("nonexistent.key", "cz")
# Vrátí: "nonexistent.key" (fallback na samotný klíč)
```

**Frontend:**
```javascript
// Translation manager má stejné chování
const text = window.translationManager.get("missing.key");
// Vrátí: "missing.key"

// V UI se zobrazí klíč místo prázdného prostoru
<span data-key="missing.key">missing.key</span>
```

**Debug režim:**
```javascript
if (DEBUG_MODE) {
    // Highlight missing translations
    document.querySelectorAll('[data-key]').forEach(el => {
        const key = el.getAttribute('data-key');
        const translation = window.translationManager.get(key);
        
        if (translation === key) {
            // Translation chybí
            el.style.border = '2px solid red';
            console.warn(`Missing translation for: ${key}`);
        }
    });
}
```

---

## Scénář 10: Persistence po Restartu

**Situace:** Server se restartuje, custom labels musí přežít.

**Při startu serveru:**
```python
# V main.py nebo startup event
@app.on_event("startup")
async def load_translations():
    # Load translation files do cache
    from app.translations import load_translations
    
    load_translations("czech")
    load_translations("iris")
    
    print("✓ Translations loaded into cache")

# Při připojení uživatele
@router.get("/api/translations/")
async def get_translations():
    # Custom labels se načtou z DB
    custom_labels = db.query(CustomLabel).all()
    custom_dict = {label.key: label.value for label in custom_labels}
    
    # Vrátit klientovi
    return {
        "translations": load_translations(language_mode),
        "custom_labels": custom_dict,
        "language_mode": system_settings.language_mode
    }
```

**Klient po reconnect:**
```javascript
// Po reconnect k serveru
socket.on('connect', async () => {
    // Reload překlady včetně custom labels
    await window.translationManager.init();
    
    // UI se obnoví se správnými custom názvy
});
```

---

## Testing Checklist

- [ ] Načtení default czech translations
- [ ] Přepnutí do czech-iris režimu
- [ ] Nastavení custom label
- [ ] Custom label přežije refresh stránky
- [ ] Multi-tab synchronizace funguje
- [ ] Reset custom labels vrátí default
- [ ] Real-time language switch funguje
- [ ] Fallback na klíč když translation chybí
- [ ] Nested HTML elementy se správně aktualizují
- [ ] Custom labels mají nejvyšší prioritu

---

**Poznámka:** Všechny tyto příklady předpokládají dokončenou implementaci podle INTEGRATION_GUIDE.md.
