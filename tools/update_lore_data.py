import json
from pathlib import Path

BASE_DIR = Path("doc/iris/lore-web/data")
ROLES_FILE = BASE_DIR / "roles.json"
MANUALS_FILE = BASE_DIR / "manuals.json"

def update_roles():
    if not ROLES_FILE.exists():
        print("Roles file not found!")
        return

    with open(ROLES_FILE, 'r') as f:
        roles = json.load(f)
        
    for role in roles:
        # Determine avatar
        avatar = "avatar_user_male.png" # Default
        
        if role['type'] == 'admin':
            avatar = "avatar_admin.png"
        elif role['type'] == 'agent':
            avatar = "avatar_agent.png"
        else: # user
            name = role['name'].split()[0].lower()
            if name in ['jana', 'simona', 'marie', 'petra', 'ema', 'tereza', 'lenka']:
                avatar = "avatar_user_female.png"
            elif name in ['karel', 'tuan', 'ivan', 'lukáš', 'lukas']:
                avatar = "avatar_user_male.png"
        
        role['avatar'] = avatar
        
    with open(ROLES_FILE, 'w') as f:
        json.dump(roles, f, indent=4, ensure_ascii=False)
    print("Roles updated with avatars.")

def create_manuals():
    content = {
        "user": {
            "title": "Příručka pro Uživatele (Subjekty)",
            "content": """
                <h1>IRIS Systém - Příručka pro Uživatele</h1>
                <p><strong>Dokumentace:</strong> IRIS 4.0 aktuální k HLINIK Phase 34</p>
                
                <div class="manual-image-container">
                    <img src="assets/images/infographic_mechanics.png" alt="Small Universe Diagram" class="manual-img">
                    <p class="img-caption">Schéma 1: Architektura Small Universe systému a interakce stanic.</p>
                </div>
                
                <h2>1. Úvod</h2>
                <p>IRIS je komunikační systém pro LARP hru, kde vy jako subjekt (uživatel) komunikujete s agentem prostřednictvím terminálu. Systém simuluje dystopickou korporátní AI infrastrukturu.</p>
                
                <h3>Vaše role</h3>
                <p>Jako <strong>Subjekt (User)</strong> jste běžný hráč, který:</p>
                <ul>
                    <li>Komunikuje s přiděleným agentem</li>
                    <li>Plní úkoly za kredity</li>
                    <li>Může nahlásit anomálie ve zprávách</li>
                </ul>
                
                <h2>2. Přihlášení do systému</h2>
                <table>
                    <tr><th>Pole</th><th>Hodnota</th></tr>
                    <tr><td>Uživatel</td><td>user1 až user8</td></tr>
                    <tr><td>Heslo</td><td>sdělí organizátoři</td></tr>
                </table>
                
                <h2>3. Rozhraní terminálu</h2>
                <h3>Levý panel - Stav subjektu</h3>
                <ul>
                    <li><strong>POSUN SVĚTA:</strong> Aktuální časový posun (0-7)</li>
                    <li><strong>KREDITY:</strong> Vaše virtuální měna</li>
                </ul>
                
                <h2>4. Práce s úkoly</h2>
                <table>
                    <tr><th>Stav</th><th>Význam</th></tr>
                    <tr><td>ČEKÁ NA SCHVÁLENÍ</td><td>Požádali jste o úkol, správce jej musí schválit</td></tr>
                    <tr><td>AKTIVNÍ</td><td>Úkol je přidělen, můžete na něm pracovat</td></tr>
                    <tr><td>DOKONČENO</td><td>Úkol jste odevzdali</td></tr>
                </table>
                
                <h2>5. Speciální stavy</h2>
                <ul>
                    <li><strong>Purgatory:</strong> Pokud máte záporné kredity, chat je zablokován</li>
                    <li><strong>Glitch:</strong> Vizuální efekt při přetížení systému</li>
                </ul>
            """
        },
        "agent": {
            "title": "Příručka pro Agenty (Operátory)",
            "content": """
                <h1>IRIS Systém - Příručka pro Agenty</h1>
                <p><strong>Dokumentace:</strong> IRIS 4.0 aktuální k HLINIK Phase 34</p>
                
                <div class="manual-image-container">
                    <img src="assets/images/infographic_relations.png" alt="Relations Graph" class="manual-img">
                    <p class="img-caption">Schéma 2: Síť vztahů 'Kdo, Koho, Proč' - vizualizace sociálních vazeb.</p>
                </div>
                
                <h2>1. Úvod</h2>
                <p>Jako <strong>Agent (Operátor)</strong> jste odpovědní za komunikaci se subjekty (běžnými hráči). Odpovídáte na jejich zprávy a pomáháte jim v rámci herního světa.</p>
                
                <h3>Vaše role</h3>
                <ul>
                    <li>Odpovídáte na zprávy od přidělených subjektů</li>
                    <li>Musíte reagovat včas (sledujte časovač)</li>
                    <li>Můžete využít AI asistenci (Autopilot)</li>
                </ul>
                
                <h2>2. Rozhraní agenta</h2>
                <h3>Levý panel - Status</h3>
                <ul>
                    <li><strong>CÍLOVÝ POSUN SVĚTA:</strong> Zobrazuje aktuální shift hodnotu</li>
                    <li><strong>STAV PŘIPOJENÍ:</strong> Ukazuje vaše ID relace</li>
                    <li><strong>ČASOVAČ ODPOVĚDI:</strong> Žlutý pruh ukazuje zbývající čas</li>
                </ul>
                
                <h2>3. Komunikace se subjekty</h2>
                <ul>
                    <li>Zprávy od subjektů se zobrazují automaticky</li>
                    <li>Nová zpráva spustí časovač odpovědi</li>
                    <li>Musíte odpovědět včas, jinak se vstup zablokuje</li>
                </ul>
                
                <h2>4. Autopilot a AI</h2>
                <ul>
                    <li><strong>TOGGLE AUTOPILOT:</strong> Aktivuje automatický režim odpovídání</li>
                    <li><strong>AI Optimalizace:</strong> Vaše zprávy mohou být přepsány AI</li>
                </ul>
            """
        },
        "admin": {
            "title": "Příručka pro Správce (Adminy)",
            "content": """
                <h1>IRIS Systém - Příručka pro Správce</h1>
                <p><strong>Dokumentace:</strong> IRIS 4.0 aktuální k HLINIK Phase 34</p>
                
                <div class="manual-image-container">
                    <img src="assets/images/infographic_economy.png" alt="Economy Dashboard" class="manual-img">
                    <p class="img-caption">Schéma 3: Ekonomické ukazatele systému a monitoring transakcí.</p>
                </div>
                
                <h2>1. Úvod</h2>
                <p>Jako <strong>Správce (Admin)</strong> ovládáte herní mechaniky, schvalujete úkoly a dohlížíte na průběh hry.</p>
                
                <h2>2. Dashboard - Přehled stanic</h2>
                <table>
                    <tr><th>Stanice</th><th>Barva</th><th>Funkce</th></tr>
                    <tr><td>UMYVADLO</td><td>Zelená</td><td>Monitoring - sledování všech relací</td></tr>
                    <tr><td>ROZKOŠ</td><td>Žlutá</td><td>Kontrola - herní nastavení</td></tr>
                    <tr><td>BAHNO</td><td>Modrá</td><td>Ekonomika - správa kreditů</td></tr>
                    <tr><td>MRKEV</td><td>Fialová</td><td>Úkoly - schvalování a vyplácení</td></tr>
                </table>
                
                <h2>3. Stanice MONITORING</h2>
                <ul>
                    <li><strong>VŠEVIDOUCÍ:</strong> Mřížka všech 8 relací</li>
                    <li><strong>ŠUM:</strong> Pouze chat karty bez logu</li>
                    <li><strong>HISTORIE OMYLŮ:</strong> Kompletní systémový log</li>
                    <li><strong>PAVUČINA:</strong> Grafické zobrazení sítě</li>
                </ul>
                
                <h2>4. Stanice KONTROLA</h2>
                <ul>
                    <li><strong>POSUN REALITY:</strong> Ovládání shift hodnoty</li>
                    <li><strong>TLAK PÁRY:</strong> Power management</li>
                    <li><strong>HLADINA STRESU:</strong> Teplota systému</li>
                </ul>
                
                <h2>5. Stanice EKONOMIKA</h2>
                <ul>
                    <li><strong>[+]:</strong> Přidat kredity (bonus)</li>
                    <li><strong>[-]:</strong> Odebrat kredity (pokuta)</li>
                    <li><strong>[LOCK]:</strong> Zablokovat terminál</li>
                </ul>
            """
        },
        "root": {
            "title": "Příručka pro ROOT (Gamemaster)",
            "content": """
                <h1>IRIS Systém - Příručka pro ROOT</h1>
                <p><strong>Dokumentace:</strong> IRIS 4.0 aktuální k HLINIK Phase 34</p>
                
                <h2>1. Přístup do ROOT konzole</h2>
                <table>
                    <tr><th>Pole</th><th>Hodnota</th></tr>
                    <tr><td>Uživatel</td><td>root</td></tr>
                    <tr><td>Heslo</td><td>sdělí organizátoři</td></tr>
                </table>
                
                <h2>2. Panopticon - Hlavní přehled</h2>
                <h3>SYSTEM STATUS</h3>
                <ul>
                    <li><strong>SHIFT OFFSET:</strong> Aktuální hodnota posunu (0-7)</li>
                    <li><strong>ONLINE USERS:</strong> Počet připojených uživatelů</li>
                    <li><strong>CHERNOBYL:</strong> Úroveň nestability systému</li>
                </ul>
                
                <h3>PHYSICS CONSTANTS</h3>
                <ul>
                    <li><strong>TAX RATE:</strong> Procento z odměny za úkol do Treasury</li>
                    <li><strong>POWER CAP:</strong> Maximální kapacita systému v MW</li>
                </ul>
                
                <h2>3. Executive Protocols</h2>
                <table>
                    <tr><th>Tlačítko</th><th>Funkce</th></tr>
                    <tr><td>FORCE SHIFT</td><td>Zvýší shift o 1</td></tr>
                    <tr><td>GLOBAL BROADCAST</td><td>Pošle zprávu všem</td></tr>
                    <tr><td>SYSTEM RESET</td><td>Resetuje kredity, úkoly, logy</td></tr>
                    <tr><td>RESTART SERVER</td><td>Restartuje Python server</td></tr>
                    <tr><td>FACTORY RESET</td><td>Smaže DB a restartuje</td></tr>
                </table>
                
                <h2>4. AI Configuration</h2>
                <ul>
                    <li><strong>OPTIMIZER PROMPT:</strong> Text pro přepisování zpráv</li>
                    <li><strong>AUTOPILOT MODEL:</strong> Výběr modelu</li>
                    <li><strong>API KEYS:</strong> Klíče pro OpenAI, OpenRouter, Gemini</li>
                </ul>
                
                <h2>5. Panic Mode</h2>
                <p>Emergency censorship - nahrazuje odchozí zprávy LLM odpovědí. Použijte v krizových situacích.</p>
            """
        }
    }
    
    with open(MANUALS_FILE, 'w') as f:
        json.dump(content, f, indent=4, ensure_ascii=False)
    print(f"Manuals created at {MANUALS_FILE}")

if __name__ == "__main__":
    update_roles()
    create_manuals()
