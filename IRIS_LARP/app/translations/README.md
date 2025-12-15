# IRIS Translation System

## Přehled / Overview

Tento adresář obsahuje systém překladů pro IRIS aplikaci. Systém je navržen s možností přepínání jazyků v reálném čase a s podporou vlastních pojmenování pro správce.

This directory contains the translation system for the IRIS application. The system is designed with real-time language switching and custom admin naming support.

## Struktura souborů / File Structure

### `czech.json`
Základní český překlad pro **všechny** UI elementy v aplikaci. Toto je výchozí jazyk (`cz`).

**Obsahuje:**
- Překlady pro všechny části UI
- Login obrazovku
- User terminal
- Agent terminal
- Admin dashboard
- Root dashboard
- Běžné UI prvky

**Usage Priority:** Základní vrstva (Level 1)

### `english.json`
Anglické překlady pro mezinárodní hráče (`en` mode).

**Obsahuje:**
- Kompletní anglické překlady všech UI elementů
- Fallback na czech.json pokud klíč chybí

**Usage Priority:** Základní vrstva (Level 1) - alternativní jazyk

### `crazy.json`
Crazy Czech překlady pro zábavný LARP efekt (`crazy` mode).

**Obsahuje:**
- Šílené/zábavné české překlady
- Přejmenovává standardní termíny na vtipné alternativy (ÚTĚK!, ZLAŤÁKY, POKUSNÍ KRÁLÍCI)
- Fallback na czech.json pokud klíč chybí

**Usage Priority:** Základní vrstva (Level 1) - alternativní jazyk

### `iris.json`
IRIS-specifické přepisy pro admin rozhraní (`czech-iris` mode). Obsahuje **pouze rozdíly** oproti `czech.json`.

**Obsahuje:**
- Specifickou admin terminologii pro LARP
- Kreativní pojmenování stanic (UMYVADLO, ROZKOŠ, BAHNO, MRKEV)
- Stylizovanou terminologii (ŠUM, HLINÍK LOG, FOREZKA, apod.)

**Usage Priority:** Přepisová vrstva (Level 2) - používá se pokud root vybere režim `czech-iris`

**Poznámka:** Tento soubor je navržen tak, aby obsahoval pouze klíče, které se liší od `czech.json`. Pro všechny ostatní klíče se použije základní český překlad.

### Custom Admin Overrides (Level 3)
Nejvyšší priorita - uloženo v databázi. Admin může pomocí funkce "PŘEPSAT REALITU" přejmenovat libovolný text v UI. Tyto vlastní názvy:
- Přepisují jakýkoli zvolený jazyk
- Jsou perzistentní napříč přihlášeními
- Mazat se dají pouze pomocí "RESET" funkce

## Priorita načítání / Loading Priority

Systém používá následující prioritu (od nejvyšší k nejnižší):

1. **Custom Admin Labels** (z databáze) - nejvyšší priorita
2. **Language File** (`czech.json` nebo `czech-iris` režim)
3. **Hardcoded Fallback** (pokud klíč chybí)

### Příklad pro klíč `admin_dashboard.hub_station_1`:

**Scénář A - Výchozí český režim (`cz`):**
```
1. Admin override? → Pokud existuje v DB → použij
2. Jinak → czech.json["admin_dashboard"]["hub_station_1"] → "UMYVADLO"
```

**Scénář B - IRIS režim (`czech-iris`):**
```
1. Admin override? → Pokud existuje v DB → použij
2. Jinak → iris.json["admin_dashboard"]["hub_station_1"] → "UMYVADLO"
3. Pokud není v iris.json → fallback na czech.json["admin_dashboard"]["hub_station_1"]
```

**Scénář C - Admin přepsal text:**
```
1. Admin override = "SANITÁRNÍ MODUL 7" → použij vždy, bez ohledu na jazyk
```

## Strukturace klíčů / Key Structure

Klíče jsou organizovány hierarchicky podle části aplikace:

```json
{
  "section": {
    "element_key": "Přeložený text"
  }
}
```

### Sekce / Sections:
- `login` - Přihlašovací obrazovka
- `user_terminal` - Terminal pro běžné uživatele
- `agent_terminal` - Terminal pro agenty
- `admin_dashboard` - Admin ovládací panel
- `root_dashboard` - Root superadmin panel
- `common` - Společné UI elementy
- `editable_labels` - Editovatelné štítky pro správce

## Implementační poznámky / Implementation Notes

### Pro budoucí implementaci logiky:

1. **Načítání souborů:**
   - Load `czech.json` jako základ
   - Pokud režim je `czech-iris`, load `iris.json` a slouč (iris přepisuje czech)

2. **Runtime překlad:**
   ```python
   def get_translation(key_path, language_mode="cz"):
       # 1. Check DB for custom admin override
       custom = db.get_custom_label(key_path)
       if custom:
           return custom
       
       # 2. Load language file
       if language_mode == "czech-iris":
           value = iris_translations.get(key_path) or czech_translations.get(key_path)
       else:  # default "cz"
           value = czech_translations.get(key_path)
       
       # 3. Fallback
       return value or key_path
   ```

3. **Real-time switching:**
   - Root může přepnout jazyk v nastavení
   - Změna by měla okamžitě aktualizovat UI pro všechny aktivní uživatele
   - Použít WebSocket broadcast pro notifikaci změny jazyka

4. **Admin custom labels:**
   - Uložit v DB tabulce `custom_labels` (key, value)
   - Přidat UI tlačítko "PŘEPSAT REALITU" v admin dashboardu
   - Při kliknutí na text s `data-key="..."` atributem, umožnit editaci
   - Reset funkce by měla vyčistit všechny custom labels z DB

5. **HTML integrace:**
   - Použít `data-key` atributy pro identifikaci přeložitelných elementů
   - JavaScript funkce pro real-time aktualizaci textů

## Rozšiřitelnost / Extensibility

Systém podporuje 4 jazykové režimy:
- **cz** - Čeština (výchozí)
- **en** - English
- **crazy** - Crazy Čeština (LARP efekt)
- **czech-iris** - Čeština + IRIS terminologie

Pro přidání nového jazyka:
- Stačí přidat nový `.json` soubor (např. `german.json`)
- Updatovat `__init__.py` loading logiku
- Updatovat `routers/translations.py` validaci
- Přidat nový režim do root settings UI

## Testing

Pro testování překladů:
1. Ověřte, že všechny klíče v `iris.json` existují také v `czech.json`
2. Zkontrolujte, že všechny `data-key` atributy v HTML mají odpovídající klíč v překladech
3. Testujte přepínání mezi všemi režimy (`cz`, `en`, `crazy`, `czech-iris`)
4. Testujte custom admin overrides a jejich persistenci

Spuštění testů:
```bash
cd IRIS_LARP
python -m app.translations.test_translations
```

---

**Vytvořeno:** 2025-12-14  
**Aktualizováno:** 2025-12-15 (Phase 36)  
**Verze:** 1.1.0  
**Status:** ✅ Fully implemented
