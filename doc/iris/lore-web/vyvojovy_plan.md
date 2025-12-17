# Vývojový plán: Modul Generátory pro Lore-Web

Tento dokument slouží jako zadání pro implementaci nové sekce "Generátory" do aplikace lore-web. Cílem je umožnit organizátorům (a následně hráčům) spouštět předpřipravené skripty, které pomocí LLM (Gemini) generují nebo upravují herní obsah (např. profily uživatelů).

## 1. Architektura řešení

Systém se skládá ze tří hlavních částí:
1.  **Frontend (Lore-Web)**: Nová záložka v menu, Wizard UI pro konfiguraci skriptu, zobrazení průběhu (logu).
2.  **Backend (IRIS API)**: Nový router `generators_api.py`, který zajišťuje exekuci skriptů, volání LLM a zápis změn.
3.  **Data & Logy**: Úpravy JSON souborů (např. `users.json`) a ukládání logů do `doc/iris/lore-web/logs`.

---

## 2. Backend Implementace (Python)

### 2.1 Nový Router `app/routers/generators_api.py`

Vytvořit nový soubor `generators_api.py`. Tento router bude obsahovat endpointy pro seznam dostupných skriptů a jejich spouštění.

**Klíčové komponenty:**
*   **Seznam skriptů**: Hardcoded seznam (pro MVP) nebo scan adresáře. Pro začátek implementovat skript `update_user_profile`.
*   **Logování**: Funkce pro zápis textového logu do `doc/iris/lore-web/logs/<timestamp>_<script_name>.log`.
*   **LLM Integrace**: Použití existujícího `app.logic.llm_core.llm_service`.

**Endpointy:**

1.  `GET /api/generators/scripts`
    *   Vrátí seznam dostupných skriptů (ID, název, popis, požadované vstupy).
    *   Příklad skriptu:
        ```json
        {
          "id": "update_user_profile",
          "name": "Aktualizace profilu uživatele",
          "description": "Vygeneruje a přepíše občanské jméno a popisy uživatele na základě jeho role a archetypu.",
          "inputs": [
            {"type": "select", "name": "user_id", "source": "users", "label": "Vyber uživatele"},
            {"type": "prompt_editor", "name": "system_prompt", "label": "Systémový prompt", "default": "..."}
          ]
        }
        ```

2.  `POST /api/generators/run`
    *   Spustí konkrétní skript.
    *   **Body**: `{ "script_id": "...", "inputs": { ... } }`
    *   **Proces**:
        1.  Vytvoří log soubor.
        2.  Podle `script_id` vybere logiku.
        3.  Pro `update_user_profile`:
            *   Načte data uživatele (`users.json`).
            *   Sestaví prompt (včetně historie/kontextu z JSONU).
            *   Zavolá `llm_service` (Google Gemini via OpenRouter).
            *   Parsuje odpověď (očekává JSON).
            *   Aktualizuje `users.json` (použijte logiku z `lore_editor_api._write_json`).
        4.  Zapíše výsledek do logu.
        5.  Vrátí výsledek a cestu k logu.

### 2.2 Změny v `app/main.py`
*   Importovat nový router: `from .routers import generators_api`
*   Zaregistrovat router: `app.include_router(generators_api.router)`

---

## 3. Frontend Implementace (HTML/JS)

### 3.1 Úpravy `doc/iris/lore-web/index.html`
*   **Menu**: Do `#submenuBar` pod kategorii `lore` přidat novou položku:
    ```html
    <a href="#generators" class="submenu-link" data-section="generators">
        <span class="submenu-icon">⚡</span> Generátory
    </a>
    ```
*   **Sekce**: Přidat novou sekci `<section id="section-generators" class="content-section">`.
    *   Obsah:
        *   **Výběr skriptu**: Karty nebo seznam dostupných skriptů.
        *   **Wizard kontejner**: Dynamicky generovaný formulář pro vstupy (Hidden by default).
        *   **Log konsole**: `<pre id="scriptLog" class="log-console">` pro výpis průběhu.

### 3.2 Úpravy `doc/iris/lore-web/app.js`

*   **Navigace**: Přidat `generators` do `sectionCategories` (mapování na `lore`).
*   **Logika Wizardu**:
    *   Funkce `initGenerators()`: Načte seznam skriptů z API.
    *   Funkce `openScriptWizard(scriptId)`: Zobrazí formulář podle definice `inputs` ze skriptu.
        *   Pro `source: "users"` použít `usersData` pro naplnění selectu.
    *   Funkce `runScript()`:
        *   Odešle POST na `/api/generators/run`.
        *   Zobrazí "Loading..." nebo simulovaný log v konzoli.
        *   Po dokončení zobrazí výsledek z logu.
*   **Zobrazení Logu**: Jednoduchý polling nebo zobrazení návratové hodnoty (text logu) po dokončení requestu.

---

## 4. LLM Logika (Skript `update_user_profile`)

*   **Model**: Gemini 2.5 Flash (dle zadání, via OpenRouter).
*   **Prompt**:
    *   Poskytnout LLM kompletní JSON profil uživatele (bez citlivých dat jako password).
    *   Instrukce: "Jsi kreativní spisovatel pro LARP. Na základě archetypu a schopností vygeneruj: 1. Civilní jméno (české), 2. Krátký popis (1 věta), 3. Dlouhý popis (odstavec). Výstup pouze JSON."
*   **Zpracování**:
    *   Validovat JSON z LLM.
    *   Update polí: `obcanske_jmeno`, `kratky_popis`, `popis_html` (nebo long desc field).

## 5. Postup nasazení

1.  Implementovat backend (`generators_api.py`, `main.py`).
2.  Restartovat server `IRIS_LARP`.
3.  Implementovat frontend (`index.html`, `app.js`).
4.  Testovat:
    *   Otevřít sekci Generátory.
    *   Vybrat "Aktualizace profilu".
    *   Vybrat Usera (např. U01).
    *   Spustit.
    *   Ověřit změnu jména v sekci "Uživatelé".
    *   Zkontrolovat existenci logu v `doc/iris/lore-web/logs`.

---

## Poznámky
*   Při implementaci využijte existující CSS třídy z `style.css` pro konzistentní vzhled (tlačítka `btn-primary`, karty `dashboard-card`, vstupy `audit-input`).
*   Logy by měly být čitelné pro člověka (obsahovat časová razítka a kroky procesu).
