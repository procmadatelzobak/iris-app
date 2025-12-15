# Phase 36: Language System Enhancement - Hlinik Multi-Language Support
**Status:** ✅ COMPLETE & VERIFIED  
**Started:** 2025-12-15  
**Verified:** 2025-12-15  
**Goal:** Add multi-language support to IRIS/Hlinik system with Czech, English, and Crazy Czech options

---

## 📋 Overview

Phase 36 implements enhanced language system for the Hlinik terminal network:

1. **New Language Options** - Added English and Crazy Czech languages
2. **Root Language Control** - Root can set system language for all terminals
3. **Language Propagation** - All terminals follow root's language setting
4. **Admin Custom Labels** - Admin custom labels are preserved across language changes

---

## 🎯 Implementation Details

### Language Modes

| Mode | Label | Description |
|------|-------|-------------|
| `cz` | Čeština (výchozí) | Standard Czech translations |
| `en` | English | English translations for international players |
| `crazy` | Crazy Čeština 🤪 | Fun/crazy Czech variant for LARP effect |
| `czech-iris` | Čeština + IRIS Terminologie | LARP-specific terminology (UMYVADLO, BAHNO, etc.) |

### Files Created/Modified

| File | Purpose |
|------|---------|
| `app/translations/english.json` | Full English translations |
| `app/translations/crazy.json` | Crazy Czech translations |
| `app/translations/__init__.py` | Updated `get_translation()` for new modes |
| `app/routers/translations.py` | Updated API for new language modes |
| `app/templates/admin/root_dashboard.html` | Updated UI with all 4 language options |
| `app/translations/test_translations.py` | Added tests for new languages |

### Language Propagation Flow

1. **Root sets language** → POST `/api/translations/language`
2. **Server updates gamestate** → `gamestate.language_mode = new_mode`
3. **WebSocket broadcast** → `{type: "language_change", language_mode: "..."}`
4. **All terminals receive update** → `translationManager.handleTranslationUpdate(data)`
5. **UI refreshes** → Translations reloaded from server

### Admin Custom Labels Behavior

> [!IMPORTANT]
> Custom labels have **highest priority** in translation lookup, which means:
> - **Přejmenovaná tlačítka** (custom labels) zůstávají zachována i po změně jazyka
> - **Nepřejmenovaná tlačítka** se změní dle aktuálně zvoleného jazyka

**Translation Priority Order:**
1. ✅ `custom_labels` (admin overrides) - **HIGHEST PRIORITY**
2. ✅ Language translations (crazy/cz/en)
3. ✅ Key path fallback

Custom labels are stored per-key in `gamestate.custom_labels`. When language changes:
- Custom labels remain unchanged
- Only elements WITHOUT custom labels update to new language
- Admins can reset all custom labels via ROOT dashboard

---

## 🎨 Crazy Czech Highlights

The Crazy Czech (`crazy`) mode provides humorous translations for LARP immersion:

| Original | Crazy Version |
|----------|---------------|
| IDENTIFIKÁTOR | PŘEZDÍVKA KÁMOŠE |
| HESLO | TAJNÉ ZAKLÍNADLO |
| ODHLÁSIT | ÚTĚK! |
| KREDITY | ZLAŤÁKY |
| SYSTÉMOVÉ PŘETÍŽENÍ | SYSTÉM HOŘÍ |
| STÍN | PŘÍZRAK |
| SUBJEKTY | POKUSNÍ KRÁLÍCI |

---

## 🚀 Usage

### For Root User

1. Login as ROOT
2. Navigate to CONFIG tab
3. Find "NASTAVENÍ JAZYKA" section
4. Select language from dropdown
5. Language changes immediately for all connected terminals

### API Endpoints

```bash
# Get available language options
GET /api/translations/language-options

# Set language (root only)
POST /api/translations/language
Body: {"language_mode": "crazy"}

# Get translations for current mode
GET /api/translations/
```

---

## 🧪 Testing

### Unit Tests

```bash
cd IRIS_LARP
python3 -m app.translations.test_translations
```

### Verified Test Results (2025-12-15)

```
✓ czech.json is valid JSON
✓ iris.json is valid JSON
✓ english.json is valid JSON
✓ crazy.json is valid JSON
✓ All required sections present
Czech translations: 219 keys
IRIS overrides: 38 keys
✓ crazy mode: login.username_label = 'PŘEZDÍVKA KÁMOŠE'
✓ crazy mode: user_terminal.logout = 'ÚTĚK!'
✓ Custom override works: 'CUSTOM STATION NAME'
✓ Non-overridden key works: 'IDENTIFIKÁTOR'
============================================================
✓ All tests completed!
```

### Manual Testing

1. Login as ROOT, switch to CONFIG tab
2. Change language to "Crazy Čeština"
3. Verify UI updates with crazy translations
4. Open another terminal (agent/user) and verify language matches
5. Switch to English and verify English translations appear
6. **NEW:** Verify custom-labeled buttons remain unchanged after language switch

---

## 📚 References

- [translations/__init__.py](../app/translations/__init__.py) - Translation loading logic
- [translations/czech.json](../app/translations/czech.json) - Base Czech translations
- [translations/english.json](../app/translations/english.json) - English translations
- [translations/crazy.json](../app/translations/crazy.json) - Crazy Czech translations
- [root_dashboard.html](../app/templates/admin/root_dashboard.html) - Language settings UI

---

**Last Updated:** 2025-12-15
