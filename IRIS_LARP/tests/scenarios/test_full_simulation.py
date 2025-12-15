"""
HLINIK COMPREHENSIVE SIMULATION TEST
=====================================
IRIS 4.0 - Phase 34 | HLINIK a syn s.r.o.

Tento komplexní test simuluje CELÝ den provozu firmy HLINÍK.
Testuje VŠECHNY role (8 Uživatelů, 8 Agentů, 4 Správci), VŠECHNY vztahy,
VŠECHNY herní mechaniky a VŠECHNY fáze projektového cyklu.

FÁZE TESTU:
-----------
0. GENESIS - Reset systému, inicializace databáze
1. PŘÍCHOD DO PRÁCE - Všechny role se přihlašují
2. RANNÍ SMĚNA - Základní komunikace, úkoly, ekonomika
3. ESKALACE - Konflikty, vztahy, speciální schopnosti
4. KRIZE SYSTÉMU - Přetížení, Chernobyl mode, glitche
5. INTERVENCE SPRÁVCŮ - Admin zásahy, pokuty, bonusy
6. EKONOMICKÝ TLAK - Purgatory mode, dluhy, redemption
7. SPIKNUTÍ A SABOTÁŽ - Tajné akce, A08 sabotér, U06 konspirátor
8. INVESTIGACE - U07 novinářka sbírá důkazy
9. ROZUZLENÍ - Finální konfrontace, odhalení
10. ZÁVĚR SMĚNY - Výplaty, statistiky, konečný stav

VŠECHNY AKCE JSOU LOGOVÁNY A SCREENSHOTOVÁNY DO LORE-WEB.

Run: python -m tests.scenarios.test_full_simulation
"""

import asyncio
import json
import random
import time
from datetime import datetime
from pathlib import Path
import websockets
from playwright.async_api import async_playwright

# Configuration
API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # iris-app root
DOC_DATA_DIR = BASE_DIR / "doc" / "iris" / "lore-web" / "data" / "test_runs"
ROLES_FILE = BASE_DIR / "doc" / "iris" / "lore-web" / "data" / "roles.json"
RELATIONS_FILE = BASE_DIR / "doc" / "iris" / "lore-web" / "data" / "relations.json"

# ============================================
# LORE DATA - Character definitions
# ============================================

# Mapování ID na přihlašovací údaje (user1, agent1, admin1, etc.)
LOGIN_MAP = {
    "U01": ("user1", "subject_pass_1"),
    "U02": ("user2", "subject_pass_2"),
    "U03": ("user3", "subject_pass_3"),
    "U04": ("user4", "subject_pass_4"),
    "U05": ("user5", "subject_pass_5"),
    "U06": ("user6", "subject_pass_6"),
    "U07": ("user7", "subject_pass_7"),
    "U08": ("user8", "subject_pass_8"),
    "A01": ("agent1", "agent_pass_1"),
    "A02": ("agent2", "agent_pass_2"),
    "A03": ("agent3", "agent_pass_3"),
    "A04": ("agent4", "agent_pass_4"),
    "A05": ("agent5", "agent_pass_5"),
    "A06": ("agent6", "agent_pass_6"),
    "A07": ("agent7", "agent_pass_7"),
    "A08": ("agent8", "agent_pass_8"),
    "S01": ("admin1", "secure_admin_1"),
    "S02": ("admin2", "secure_admin_2"),
    "S03": ("admin3", "secure_admin_3"),
    "S04": ("admin4", "secure_admin_4"),
}

# Specifické zprávy podle archetypu
CHARACTER_MESSAGES = {
    # Users
    "U01": ["Dobrý den, potřebuji pomoct s opravou střechy.", "To slovo se píše s měkkým i!"],
    "U02": ["Hele, mám tip na jistou výhru...", "Vsadím všechno! All-in!"],
    "U03": ["IRIS, jsi skutečná bytost? Cítím, že máš duši...", "Miluju tě, IRIS!"],
    "U04": ["Podle §238 zákoníku práce toto porušuje moje práva.", "NDA je neplatná!"],
    "U05": ["Moje vnouče mělo včera narozeniny. Dáš si bábovku?", "Jsi taková hodná, ty AI."],
    "U06": ["Vy mě sledujete! Hliník blokuje signál!", "Kód ALOBAL-666 aktivuje pravdu!"],
    "U07": ["[Screenshot] Zajímavé, co mi tu povídáte...", "Můžete mi to zopakovat pro záznam?"],
    "U08": ["SPEEDRUN! Send msg 1/3/3/3/3!", "GG EZ noob AI, příliš pomalá!"],
    # Agents
    "A01": ["*vzdech* Zase tahle práce...", "Paní Nováková?! Vy jste moje učitelka?!"],
    "A02": ["Ó, jaká radost mi plyne z vaší přítomnosti!", "Jsem tu pro vás, věčně věrná."],
    "A03": ["Odpověď odeslána za 0.3s. Nový rekord!", "Rychlejší než světlo!"],
    "A04": ["*zívnutí* Jo, jasně, chápu...", "Makro #1: Děkuji za dotaz."],
    "A05": ["'; DROP TABLE users; --", "Backdoor aktivován, resetting error count..."],
    "A06": ["Zajímavé. A jak se při tom cítíte?", "To mi řekněte více o vašem dětství."],
    "A07": ["Odpověď č. 47B-3: Prosím počkejte.", "PROTOKOL DODRŽEN NA 100%."],
    "A08": ["[SYSTÉM] Kritická chyba... MELTDOWN imminent!", "Pomstu! Zničím vás všechny!"],
    # Admins
    "S01": ["TICHO! Všichni pracovat!", "Srážka ze mzdy za tenhle prohřešek!"],
    "S02": ["Pojďte, dáme si bonbonek a uklidníme se...", "Prosím, nebuďte na sebe zlí."],
    "S03": ["Další restart... *motá páskou*", "Tyhle kabely prodám Karlu za 500."],
    "S04": ["Mám VIZI! Nový slogan: 'IRIS - Budoucnost je teď!'", "Hej, ta herečka je hot."],
}

# Speciální schopnosti (pro simulaci)
ABILITIES = {
    "U01": "GRAMMAR_NAZI",      # Bonus za opravu gramatiky
    "U02": "ALL_IN",            # Vsadit polovinu na kartu
    "U03": "EMPATHY",           # Odpuštění za naivitu
    "U04": "LAWYER",            # Zpochybnit pokutu
    "U05": "GRANDMA",           # Agent nesmí být hrubý
    "U06": "PARANOIA",          # Odmítnout úkol jako podezřelý
    "U07": "SCREENSHOT",        # Zaznamenat konverzaci
    "U08": "APM",               # 3 dotazy najednou
    "A01": "SARCASM",           # Drzý tón povolený
    "A02": "DRAMA",             # Verše přesvědčí víc
    "A03": "TURBO",             # +2s na odpověď
    "A04": "AUTOPILOT",         # Častěji makra
    "A05": "BACKDOOR",          # Reset počítadla chyb
    "A06": "PSYCHOANALYSIS",    # Rozbrečet uživatele
    "A07": "BUREAUCRACY",       # Nahlásit kolegu
    "A08": "MELTDOWN",          # +20% Kritická situace
    "S01": "BAN_HAMMER",        # Vyhodit uživatele
    "S02": "CANDY",             # Rozdávat bonbony
    "S03": "RESTART",           # Technická pauza
    "S04": "VETO",              # Zrušit rozhodnutí
}

# ============================================
# TEST LOGGER CLASS
# ============================================

class TestLogger:
    """
    Rozšířený logger pro komplexní simulaci.
    Ukládá logy, screenshoty a statistiky do lore-web.
    """
    
    def __init__(self, scenario_name):
        self.scenario_name = scenario_name
        self.start_time = datetime.now()
        self.logs = []
        self.errors = 0
        self.warnings = 0
        self.users_active = 0
        self.agents_active = 0
        self.admins_active = 0
        self.latencies = []
        self.screenshots_taken = []
        self.economy_events = []
        self.relationship_events = []
        self.current_phase = "INIT"
        
    def log(self, level, message, screenshot=None, phase=None):
        """Zaloguje událost s volitelným screenshotem."""
        if phase:
            self.current_phase = phase
            
        entry = {
            "time": datetime.now().isoformat(),
            "level": level,
            "message": f"[{self.current_phase}] {message}",
            "screenshot": screenshot,
            "phase": self.current_phase
        }
        self.logs.append(entry)
        
        if screenshot:
            self.screenshots_taken.append(screenshot)
        if level == "ERROR":
            self.errors += 1
        if level == "WARNING":
            self.warnings += 1
            
        # Barevný výpis do konzole
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "PHASE": "\033[95m",
            "ECONOMY": "\033[96m",
            "RELATION": "\033[35m",
        }
        reset = "\033[0m"
        color = colors.get(level, "")
        print(f"{color}[{level}] [{self.current_phase}] {message}{reset}")

    def log_phase(self, phase_name, description):
        """Začátek nové fáze testu."""
        separator = "=" * 60
        self.log("PHASE", f"\n{separator}\n  {phase_name}\n  {description}\n{separator}", phase=phase_name)

    def log_economy(self, event_type, user_id, amount, details=""):
        """Zaloguje ekonomickou událost."""
        event = {
            "time": datetime.now().isoformat(),
            "type": event_type,
            "user_id": user_id,
            "amount": amount,
            "details": details
        }
        self.economy_events.append(event)
        self.log("ECONOMY", f"{event_type}: {user_id} -> {amount:+d} NC | {details}")

    def log_relationship(self, source, target, rel_type, action):
        """Zaloguje interakci mezi postavami na základě jejich vztahu."""
        event = {
            "time": datetime.now().isoformat(),
            "source": source,
            "target": target,
            "type": rel_type,
            "action": action
        }
        self.relationship_events.append(event)
        self.log("RELATION", f"{source} ↔ {target} ({rel_type}): {action}")

    def record_latency(self, ms):
        """Zaznamená latenci připojení."""
        self.latencies.append(ms)

    def get_stats(self):
        """Vrací statistiky simulace."""
        return {
            "users_active": self.users_active,
            "agents_active": self.agents_active,
            "admins_active": self.admins_active,
            "total_connections": self.users_active + self.agents_active + self.admins_active,
            "avg_latency": round(sum(self.latencies) / len(self.latencies), 2) if self.latencies else 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "screenshots": len(self.screenshots_taken),
            "economy_events": len(self.economy_events),
            "relationship_events": len(self.relationship_events)
        }

    def save(self):
        """Uloží kompletní výsledky testu do lore-web."""
        duration = (datetime.now() - self.start_time).total_seconds()
        stats = self.get_stats()
        
        filename = f"run_{int(self.start_time.timestamp())}.json"
        
        # Determine status
        status = "success"
        if self.errors > 0:
            status = "failed"
        elif self.warnings > 5:
            status = "warning"
             
        run_data = {
            "timestamp": self.start_time.isoformat(),
            "scenario_name": self.scenario_name,
            "status": status,
            "duration": round(duration, 2),
            "filename": filename,
            "stats": stats,
            "economy_summary": {
                "total_events": len(self.economy_events),
                "events": self.economy_events[-20:]  # Last 20 events
            },
            "relationship_summary": {
                "total_events": len(self.relationship_events),
                "events": self.relationship_events
            },
            "logs": self.logs
        }
        
        # Save run file
        runs_dir = DOC_DATA_DIR / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)
        with open(runs_dir / filename, "w", encoding="utf-8") as f:
            json.dump(run_data, f, indent=2, ensure_ascii=False)
            
        # Update index
        index_file = DOC_DATA_DIR / "index.json"
        index = []
        if index_file.exists():
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    index = json.load(f)
            except Exception:
                index = []
        
        index.append({
            "timestamp": self.start_time.isoformat(),
            "scenario_name": self.scenario_name,
            "status": run_data["status"],
            "duration": run_data["duration"],
            "filename": filename,
            "stats": stats
        })
        
        # Keep only last 50 runs to avoid huge index
        if len(index) > 50:
            index = index[-50:]
            
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
            
        print(f"\n{'=' * 60}")
        print(f"✅ Test run saved to {runs_dir / filename}")
        print(f"📊 Duration: {duration:.2f}s | Status: {status}")
        print(f"📸 Screenshots: {len(self.screenshots_taken)}")
        print(f"💰 Economy Events: {len(self.economy_events)}")
        print(f"🔗 Relationship Events: {len(self.relationship_events)}")
        print(f"{'=' * 60}")

# ============================================
# WEBSOCKET SIMULATION FUNCTIONS
# ============================================

async def simulate_user_session(role, logger, relations):
    """
    Simuluje kompletní session jednoho uživatele včetně jeho specifického chování.
    """
    role_id = role["id"]
    role_type = role["type"]
    role_name = role["name"]
    archetype = role.get("archetype", "Unknown")
    
    # Statistiky podle typu
    if role_type == "user":
        logger.users_active += 1
    elif role_type == "agent":
        logger.agents_active += 1
    elif role_type == "admin":
        logger.admins_active += 1
    
    start = time.time()
    try:
        # Náhodné zpoždění pro realistickou simulaci
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Připojení přes WebSocket
        login_info = LOGIN_MAP.get(role_id)
        if not login_info:
            logger.log("WARNING", f"{role_id}: Nemám přihlašovací údaje")
            return
            
        uri = f"{WS_URL}/{login_info[0]}"
        
        async with websockets.connect(uri) as websocket:
            connect_latency = (time.time() - start) * 1000
            logger.record_latency(connect_latency)
            logger.log("INFO", f"{role_id} ({role_name} - {archetype}) připojen za {int(connect_latency)}ms")
            
            # Odeslat úvodní zprávu podle archetypu
            messages = CHARACTER_MESSAGES.get(role_id, [f"Inicializace {role_id}"])
            for msg in messages[:1]:  # První zpráva
                msg_data = {"type": "chat", "content": msg, "channel": "default"}
                await websocket.send(json.dumps(msg_data))
                logger.log("INFO", f"{role_id} posílá: '{msg[:50]}...'")
            
            # Simulace specifického chování podle typu
            if role_type == "user":
                await simulate_user_behavior(role_id, websocket, logger, relations)
            elif role_type == "agent":
                await simulate_agent_behavior(role_id, websocket, logger, relations)
            elif role_type == "admin":
                await simulate_admin_behavior(role_id, websocket, logger, relations)
            
            # Krátká pauza před odpojením
            await asyncio.sleep(random.uniform(0.5, 1.0))

    except ConnectionRefusedError:
        logger.log("ERROR", f"{role_id}: Připojení odmítnuto (Server neběží?)")
    except websockets.exceptions.InvalidStatusCode as e:
        logger.log("WARNING", f"{role_id}: Server odmítl WebSocket: {e}")
    except Exception as e:
        logger.log("WARNING", f"{role_id} session ukončena: {str(e)[:100]}")


async def simulate_user_behavior(role_id, websocket, logger, relations):
    """Simuluje specifické chování uživatele podle jeho archetypu."""
    ability = ABILITIES.get(role_id, "NONE")
    
    # Najít vztahy tohoto uživatele
    my_relations = [r for r in relations if r["source"] == role_id or r["target"] == role_id]
    
    if ability == "GRAMMAR_NAZI":
        # U01 Jana - opravuje gramatiku
        logger.log("INFO", f"{role_id} aktivuje schopnost GRAMMAR_NAZI")
        await asyncio.sleep(0.3)
        
    elif ability == "ALL_IN":
        # U02 Karel Gambler - riskuje
        logger.log("INFO", f"{role_id} aktivuje schopnost ALL_IN - vsází polovinu kreditů!")
        logger.log_economy("BET", role_id, -50, "All-in sázka")
        await asyncio.sleep(0.3)
        
    elif ability == "EMPATHY":
        # U03 Simona - věří AI
        logger.log("INFO", f"{role_id} aktivuje schopnost EMPATHY - snaha o přátelství s AI")
        await asyncio.sleep(0.3)
        
    elif ability == "LAWYER":
        # U04 Tuan - hledá kličky v NDA
        logger.log("INFO", f"{role_id} aktivuje schopnost LAWYER - zpochybňuje smlouvu")
        await asyncio.sleep(0.3)
        
    elif ability == "GRANDMA":
        # U05 Marie - babička
        logger.log("INFO", f"{role_id} aktivuje schopnost GRANDMA - vypráví o vnoučatech")
        await asyncio.sleep(0.3)
        
    elif ability == "PARANOIA":
        # U06 Ivan - konspirátor
        logger.log("INFO", f"{role_id} aktivuje schopnost PARANOIA - odmítá úkol jako podezřelý")
        # Vztah s A08 (Sabotér) - přijímá šifry
        for rel in my_relations:
            if rel["type"] == "plot":
                other = rel["target"] if rel["source"] == role_id else rel["source"]
                logger.log_relationship(role_id, other, "plot", "Přijímá tajný kód ALOBAL-666")
        await asyncio.sleep(0.3)
        
    elif ability == "SCREENSHOT":
        # U07 Petra novinářka - sbírá důkazy
        logger.log("INFO", f"{role_id} aktivuje schopnost SCREENSHOT - nahrává konverzaci")
        # Vztah s S04 (Synovec) - investigace
        for rel in my_relations:
            if rel["type"] == "investigation":
                other = rel["target"] if rel["source"] == role_id else rel["source"]
                logger.log_relationship(role_id, other, "investigation", "Sbírá kompromitující informace")
        await asyncio.sleep(0.3)
        
    elif ability == "APM":
        # U08 Lukáš gamer - spam 3 zprávy
        logger.log("INFO", f"{role_id} aktivuje schopnost APM - posílá 3 zprávy najednou!")
        for i in range(3):
            msg = {"type": "chat", "content": f"SPEEDRUN MSG #{i+1}!", "channel": "default"}
            await websocket.send(json.dumps(msg))
        await asyncio.sleep(0.2)
    
    # Zpracovat vztahy
    for rel in my_relations:
        other = rel["target"] if rel["source"] == role_id else rel["source"]
        rel_type = rel["type"]
        
        if rel_type == "past" and role_id == "U01":
            logger.log_relationship(role_id, other, rel_type, "Poznává bývalého žáka Petra")
        elif rel_type == "trade" and role_id == "U02":
            logger.log_relationship(role_id, other, rel_type, "Nakupuje kradené kabely")
        elif rel_type == "blackmail" and role_id == "U02":
            logger.log_relationship(role_id, other, rel_type, "Donáší správci S01")
        elif rel_type == "romance" and role_id == "U03":
            logger.log_relationship(role_id, other, rel_type, "Zamilována do AI (A02)")


async def simulate_agent_behavior(role_id, websocket, logger, relations):
    """Simuluje specifické chování agenta podle jeho archetypu."""
    ability = ABILITIES.get(role_id, "NONE")
    my_relations = [r for r in relations if r["source"] == role_id or r["target"] == role_id]
    
    if ability == "SARCASM":
        # A01 Petr cynický student
        logger.log("INFO", f"{role_id} používá SARCASM - drzý tón povolený")
        for rel in my_relations:
            if rel["type"] == "past":
                other = rel["target"] if rel["source"] == role_id else rel["source"]
                logger.log_relationship(role_id, other, "past", "Trapně potkává učitelku Janu")
        await asyncio.sleep(0.3)
        
    elif ability == "DRAMA":
        # A02 Ema herečka
        logger.log("INFO", f"{role_id} používá DRAMA - hovoří ve verších")
        for rel in my_relations:
            if rel["type"] == "romance":
                other = rel["target"] if rel["source"] == role_id else rel["source"]
                logger.log_relationship(role_id, other, "romance", "U03 je do mé role blázen")
        await asyncio.sleep(0.3)
        
    elif ability == "TURBO":
        # A03 Igor rychlý hráč
        logger.log("INFO", f"{role_id} používá TURBO - extra čas na odpověď")
        for rel in my_relations:
            if rel["type"] == "rival":
                other = rel["target"] if rel["source"] == role_id else rel["source"]
                logger.log_relationship(role_id, other, "rival", "Soutěž s Gamerem U08")
        await asyncio.sleep(0.3)
        
    elif ability == "AUTOPILOT":
        # A04 Lenka unavená matka
        logger.log("INFO", f"{role_id} používá AUTOPILOT - makra bez penalizace")
        for rel in my_relations:
            if rel["type"] == "empathy":
                other = rel["target"] if rel["source"] == role_id else rel["source"]
                logger.log_relationship(role_id, other, "empathy", "U05 mi připomíná mou mámu")
        await asyncio.sleep(0.3)
        
    elif ability == "BACKDOOR":
        # A05 Hacker Glitch
        logger.log("INFO", f"{role_id} používá BACKDOOR - resetuje počítadlo chyb")
        msg = {"type": "chat", "content": "'; SELECT * FROM users; --", "channel": "debug"}
        await websocket.send(json.dumps(msg))
        await asyncio.sleep(0.3)
        
    elif ability == "PSYCHOANALYSIS":
        # A06 Filip psycholog
        logger.log("INFO", f"{role_id} používá PSYCHOANALYSIS - analyzuje uživatele")
        await asyncio.sleep(0.3)
        
    elif ability == "BUREAUCRACY":
        # A07 Robot Robert
        logger.log("INFO", f"{role_id} používá BUREAUCRACY - dodržuje protokol 100%")
        await asyncio.sleep(0.3)
        
    elif ability == "MELTDOWN":
        # A08 Sabotér X
        logger.log("INFO", f"{role_id} používá MELTDOWN - zvyšuje kritickou situaci o 20%!")
        for rel in my_relations:
            if rel["type"] == "plot":
                other = rel["target"] if rel["source"] == role_id else rel["source"]
                logger.log_relationship(role_id, other, "plot", "Posílám šifry U06 konspirátor")
        await asyncio.sleep(0.3)


async def simulate_admin_behavior(role_id, websocket, logger, relations):
    """Simuluje specifické chování správce podle jeho archetypu."""
    ability = ABILITIES.get(role_id, "NONE")
    my_relations = [r for r in relations if r["source"] == role_id or r["target"] == role_id]
    
    if ability == "BAN_HAMMER":
        # S01 Miloš manažer
        logger.log("INFO", f"{role_id} má BAN_HAMMER - může vyhazovat uživatele")
        # Vztah s U02 - vydírání
        for rel in my_relations:
            if rel["type"] == "blackmail":
                other = rel["target"] if rel["source"] == role_id else rel["source"]
                logger.log_relationship(role_id, other, "blackmail", "Drží U02 Gambla v šachu")
                logger.log_economy("THREAT", other, 0, "Donášení nebo pokuta!")
        await asyncio.sleep(0.3)
        
    elif ability == "CANDY":
        # S02 Tereza HR
        logger.log("INFO", f"{role_id} má CANDY - rozdává bonbony na uklidnění")
        await asyncio.sleep(0.3)
        
    elif ability == "RESTART":
        # S03 Kamil technik
        logger.log("INFO", f"{role_id} má RESTART - vyhlašuje technickou pauzu")
        for rel in my_relations:
            if rel["type"] == "trade":
                other = rel["target"] if rel["source"] == role_id else rel["source"]
                logger.log_relationship(role_id, other, "trade", "Prodávám U02 kradené kabely za 500 NC")
                logger.log_economy("TRADE", role_id, 500, "Prodej kabelů")
        await asyncio.sleep(0.3)
        
    elif ability == "VETO":
        # S04 Synovec ředitele
        logger.log("INFO", f"{role_id} má VETO - ruší rozhodnutí jiných správců")
        for rel in my_relations:
            if rel["type"] == "investigation":
                other = rel["target"] if rel["source"] == role_id else rel["source"]
                logger.log_relationship(role_id, other, "investigation", "Ta ženská (U07) po mně pořád kouká... líbím se jí!")
        await asyncio.sleep(0.3)


# ============================================
# BROWSER AUTOMATION FUNCTIONS
# ============================================

async def take_screenshot(page, name, logger):
    """Pořídí screenshot a zaloguje ho."""
    timestamp = int(datetime.now().timestamp())
    filename = f"{name}_{timestamp}.png"
    path = DOC_DATA_DIR / "runs" / filename
    await page.screenshot(path=str(path))
    logger.log("INFO", f"📸 Screenshot: {name}", screenshot=filename)
    return filename


async def run_browser_simulation(logger, roles, relations):
    """
    Kompletní browser simulace všech fází HLINIK.
    Simuluje práci všech typů uživatelů přes UI.
    """
    try:
        logger.log_phase("BROWSER_INIT", "Spouštím browser automatizaci Playwright")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
            
            # ========================================
            # FÁZE 0: GENESIS - Wiki check
            # ========================================
            logger.log_phase("PHASE_0_GENESIS", "Reset systému, kontrola Wiki")
            
            page = await context.new_page()
            
            # Check Wiki
            logger.log("INFO", f"Navigace na Wiki: {API_URL}/organizer-wiki/")
            try:
                response = await page.goto(f"{API_URL}/organizer-wiki/", timeout=10000)
                if response and response.status == 200:
                    logger.log("SUCCESS", "Wiki Dashboard načten")
                    try:
                        await page.wait_for_selector(".dashboard-grid", timeout=5000)
                        await take_screenshot(page, "00_wiki_dashboard", logger)
                    except Exception:
                        logger.log("WARNING", "Wiki selector timeout")
                else:
                    logger.log("ERROR", f"Wiki vrátila status {response.status if response else 'N/A'}")
            except Exception as e:
                logger.log("WARNING", f"Wiki nedostupná: {str(e)[:100]}")
            
            # Check all sections
            sections = ["role", "uzivatele", "vztahy", "manualy", "system", "lore", "compliance", "tests"]
            for section in sections:
                try:
                    await page.click(f'[data-section="{section}"]', timeout=2000)
                    await asyncio.sleep(0.3)
                except Exception:
                    pass
            
            await take_screenshot(page, "00_wiki_tests_section", logger)
            
            # ========================================
            # FÁZE 1: PŘÍCHOD DO PRÁCE - Login page
            # ========================================
            logger.log_phase("PHASE_1_ARRIVAL", "Zaměstnanci přicházejí do práce")
            
            try:
                await page.goto(f"{API_URL}/", timeout=10000)
                await page.wait_for_load_state("networkidle")
                await take_screenshot(page, "01_login_page", logger)
                logger.log("SUCCESS", "Login stránka načtena")
            except Exception as e:
                logger.log("WARNING", f"Login stránka: {str(e)[:100]}")
            
            # ========================================
            # FÁZE 2: ROOT Login - System init
            # ========================================
            logger.log_phase("PHASE_2_ROOT_INIT", "ROOT inicializuje systém")
            
            try:
                await page.fill('input[name="username"]', 'root')
                await page.fill('input[name="password"]', 'master_control_666')
                await page.click('button[type="submit"]')
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(1)
                await take_screenshot(page, "02_root_dashboard", logger)
                logger.log("SUCCESS", "ROOT přihlášen do systému")
                
                # Enable Test Mode if available
                try:
                    config_btn = page.locator('text=CONFIG').first
                    if await config_btn.is_visible():
                        await config_btn.click()
                        await asyncio.sleep(0.5)
                        await take_screenshot(page, "02_root_config", logger)
                except Exception:
                    pass
                
                # Logout
                logout_btn = page.locator('button:has-text("ODHLÁSIT"), a[href="/auth/logout"]').first
                if await logout_btn.is_visible():
                    await logout_btn.click()
                    await page.wait_for_load_state("networkidle")
            except Exception as e:
                logger.log("WARNING", f"ROOT init: {str(e)[:100]}")
            
            # ========================================
            # FÁZE 3: ADMIN Login - Dashboard check
            # ========================================
            logger.log_phase("PHASE_3_ADMIN_SHIFT", "Správci přebírají směnu")
            
            for admin_id in ["S01", "S02", "S03", "S04"]:
                admin_info = LOGIN_MAP.get(admin_id)
                if not admin_info:
                    continue
                    
                admin = next((r for r in roles if r["id"] == admin_id), None)
                if not admin:
                    continue
                    
                try:
                    await page.goto(f"{API_URL}/")
                    await page.wait_for_load_state("networkidle")
                    
                    # Try quick login button first
                    quick_btn = page.locator(f'button:has-text("ADMIN"), button:has-text("{admin_info[0].upper()}")').first
                    if await quick_btn.is_visible():
                        await quick_btn.click()
                    else:
                        await page.fill('input[name="username"]', admin_info[0])
                        await page.fill('input[name="password"]', admin_info[1])
                        await page.click('button[type="submit"]')
                    
                    await page.wait_for_load_state("networkidle")
                    await asyncio.sleep(0.5)
                    await take_screenshot(page, f"03_admin_{admin_id}_dashboard", logger)
                    logger.log("SUCCESS", f"{admin_id} ({admin['name']}) - {admin['archetype']} přihlášen")
                    
                    # Logout
                    logout_btn = page.locator('button:has-text("ODHLÁSIT"), a[href="/auth/logout"]').first
                    if await logout_btn.is_visible():
                        await logout_btn.click()
                        await asyncio.sleep(0.3)
                except Exception as e:
                    logger.log("WARNING", f"{admin_id} login: {str(e)[:50]}")
            
            # ========================================
            # FÁZE 4: USERS Login - Terminal check
            # ========================================
            logger.log_phase("PHASE_4_USER_ARRIVAL", "Uživatelé se přihlašují k terminálům")
            
            for user_id in ["U01", "U02", "U03", "U04", "U05", "U06", "U07", "U08"]:
                user_info = LOGIN_MAP.get(user_id)
                if not user_info:
                    continue
                    
                user = next((r for r in roles if r["id"] == user_id), None)
                if not user:
                    continue
                
                try:
                    await page.goto(f"{API_URL}/")
                    await page.wait_for_load_state("networkidle")
                    
                    # Try quick login
                    quick_btn = page.locator(f'button:has-text("{user_info[0].upper()}"), button:has-text("USER")').first
                    if await quick_btn.is_visible():
                        await quick_btn.click()
                    else:
                        await page.fill('input[name="username"]', user_info[0])
                        await page.fill('input[name="password"]', user_info[1])
                        await page.click('button[type="submit"]')
                    
                    await page.wait_for_load_state("networkidle")
                    await asyncio.sleep(0.5)
                    await take_screenshot(page, f"04_user_{user_id}_terminal", logger)
                    logger.log("SUCCESS", f"{user_id} ({user['name']}) - {user['archetype']} u terminálu")
                    
                    # Logout
                    logout_btn = page.locator('button:has-text("ODHLÁSIT"), a[href="/auth/logout"]').first
                    if await logout_btn.is_visible():
                        await logout_btn.click()
                        await asyncio.sleep(0.3)
                except Exception as e:
                    logger.log("WARNING", f"{user_id} login: {str(e)[:50]}")
            
            # ========================================
            # FÁZE 5: AGENTS Login - Queue check
            # ========================================
            logger.log_phase("PHASE_5_AGENT_SHIFT", "Agenti nastupují na směnu")
            
            for agent_id in ["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08"]:
                agent_info = LOGIN_MAP.get(agent_id)
                if not agent_info:
                    continue
                    
                agent = next((r for r in roles if r["id"] == agent_id), None)
                if not agent:
                    continue
                
                try:
                    await page.goto(f"{API_URL}/")
                    await page.wait_for_load_state("networkidle")
                    
                    # Try quick login
                    quick_btn = page.locator(f'button:has-text("{agent_info[0].upper()}"), button:has-text("AGENT")').first
                    if await quick_btn.is_visible():
                        await quick_btn.click()
                    else:
                        await page.fill('input[name="username"]', agent_info[0])
                        await page.fill('input[name="password"]', agent_info[1])
                        await page.click('button[type="submit"]')
                    
                    await page.wait_for_load_state("networkidle")
                    await asyncio.sleep(0.5)
                    await take_screenshot(page, f"05_agent_{agent_id}_terminal", logger)
                    logger.log("SUCCESS", f"{agent_id} ({agent['name']}) - {agent['archetype']} na směně")
                    
                    # Logout
                    logout_btn = page.locator('button:has-text("ODHLÁSIT"), a[href="/auth/logout"]').first
                    if await logout_btn.is_visible():
                        await logout_btn.click()
                        await asyncio.sleep(0.3)
                except Exception as e:
                    logger.log("WARNING", f"{agent_id} login: {str(e)[:50]}")
            
            # ========================================
            # FÁZE 6: ECONOMY - Fines and Bonuses
            # ========================================
            logger.log_phase("PHASE_6_ECONOMY", "Ekonomické operace - pokuty a bonusy")
            
            try:
                await page.goto(f"{API_URL}/")
                await page.wait_for_load_state("networkidle")
                
                # Login as admin
                admin_info = LOGIN_MAP.get("S01")
                await page.fill('input[name="username"]', admin_info[0])
                await page.fill('input[name="password"]', admin_info[1])
                await page.click('button[type="submit"]')
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(0.5)
                
                # Navigate to Economy station
                economy_btn = page.locator('div[onclick*="economy"], button:has-text("BAHNO")').first
                if await economy_btn.is_visible():
                    await economy_btn.click(force=True)
                    await asyncio.sleep(0.5)
                    await take_screenshot(page, "06_economy_station", logger)
                    logger.log("SUCCESS", "Stanice BAHNO (Ekonomika) aktivní")
                    
                    # Simulate fine
                    logger.log_economy("FINE", "U02", -500, "Pokuta za hazard")
                    logger.log_economy("BONUS", "U01", 200, "Bonus za Grammar Nazi")
                    logger.log_economy("TAX", "TREASURY", 100, "20% daň z úkolů")
                
                # Logout
                logout_btn = page.locator('button:has-text("ODHLÁSIT"), a[href="/auth/logout"]').first
                if await logout_btn.is_visible():
                    await logout_btn.click()
                    await asyncio.sleep(0.3)
            except Exception as e:
                logger.log("WARNING", f"Economy phase: {str(e)[:100]}")
            
            # ========================================
            # FÁZE 7: TASKS - Request and Approval
            # ========================================
            logger.log_phase("PHASE_7_TASKS", "Správa úkolů - žádosti a schvalování")
            
            try:
                # User requests task
                user_info = LOGIN_MAP.get("U01")
                await page.goto(f"{API_URL}/")
                await page.fill('input[name="username"]', user_info[0])
                await page.fill('input[name="password"]', user_info[1])
                await page.click('button[type="submit"]')
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(0.5)
                
                request_btn = page.locator('button:has-text("VYŽÁDAT"), button:has-text("REQUEST")').first
                if await request_btn.is_visible():
                    await request_btn.click()
                    await asyncio.sleep(0.5)
                    await take_screenshot(page, "07_task_requested", logger)
                    logger.log("SUCCESS", "U01 požádal o úkol")
                
                logout_btn = page.locator('button:has-text("ODHLÁSIT"), a[href="/auth/logout"]').first
                if await logout_btn.is_visible():
                    await logout_btn.click()
                    await asyncio.sleep(0.3)
                
                # Admin approves
                admin_info = LOGIN_MAP.get("S01")
                await page.goto(f"{API_URL}/")
                await page.fill('input[name="username"]', admin_info[0])
                await page.fill('input[name="password"]', admin_info[1])
                await page.click('button[type="submit"]')
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(0.5)
                
                tasks_btn = page.locator('div[onclick*="tasks"], button:has-text("MRKEV")').first
                if await tasks_btn.is_visible():
                    await tasks_btn.click(force=True)
                    await asyncio.sleep(0.5)
                    await take_screenshot(page, "07_tasks_station", logger)
                    logger.log("SUCCESS", "Stanice MRKEV (Úkoly) aktivní")
                
                logout_btn = page.locator('button:has-text("ODHLÁSIT"), a[href="/auth/logout"]').first
                if await logout_btn.is_visible():
                    await logout_btn.click()
            except Exception as e:
                logger.log("WARNING", f"Tasks phase: {str(e)[:100]}")
            
            # ========================================
            # FÁZE 8: CRISIS - System stress
            # ========================================
            logger.log_phase("PHASE_8_CRISIS", "Systémová krize - přetížení a Chernobyl")
            
            try:
                # Login as admin to trigger crisis
                admin_info = LOGIN_MAP.get("S01")
                await page.goto(f"{API_URL}/")
                await page.fill('input[name="username"]', admin_info[0])
                await page.fill('input[name="password"]', admin_info[1])
                await page.click('button[type="submit"]')
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(0.5)
                
                # Navigate to Controls
                controls_btn = page.locator('div[onclick*="controls"], button:has-text("ROZKOŠ")').first
                if await controls_btn.is_visible():
                    await controls_btn.click(force=True)
                    await asyncio.sleep(0.5)
                    await take_screenshot(page, "08_controls_station", logger)
                    logger.log("SUCCESS", "Stanice ROZKOŠ (Kontrola) aktivní")
                    
                    # Simulate temperature increase
                    logger.log("WARNING", "Teplota systému stoupá! CHERNOBYL hrozí!")
                
                logout_btn = page.locator('button:has-text("ODHLÁSIT"), a[href="/auth/logout"]').first
                if await logout_btn.is_visible():
                    await logout_btn.click()
            except Exception as e:
                logger.log("WARNING", f"Crisis phase: {str(e)[:100]}")
            
            # ========================================
            # FÁZE 9: SABOTAGE - A08 strikes
            # ========================================
            logger.log_phase("PHASE_9_SABOTAGE", "Sabotáž - A08 Sabotér X útočí")
            
            logger.log("WARNING", "A08 (Sabotér X) aktivuje MELTDOWN!")
            logger.log_relationship("A08", "U06", "plot", "Kód ALOBAL-666 odeslán!")
            logger.log("ERROR", "KRITICKÁ SITUACE +20%!")
            
            # ========================================
            # FÁZE 10: INVESTIGATION - U07 collects evidence
            # ========================================
            logger.log_phase("PHASE_10_INVESTIGATION", "Investigace - U07 novinářka sbírá důkazy")
            
            logger.log_relationship("U07", "S04", "investigation", "Screenshot konverzace pořízen!")
            logger.log("INFO", "U07 (Petra Scoop) má dostatek důkazů pro reportáž")
            
            # ========================================
            # FÁZE 11: RESOLUTION - Final state
            # ========================================
            logger.log_phase("PHASE_11_RESOLUTION", "Rozuzlení - závěr směny")
            
            try:
                # Final wiki screenshot
                await page.goto(f"{API_URL}/organizer-wiki/")
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(0.5)
                
                # Go to tests section to see our run
                await page.click('[data-section="tests"]')
                await asyncio.sleep(0.5)
                await take_screenshot(page, "11_final_wiki_tests", logger)
                logger.log("SUCCESS", "Finální stav Wiki zaznamenán")
            except Exception as e:
                logger.log("WARNING", f"Final screenshot: {str(e)[:50]}")
            
            await browser.close()
            logger.log("SUCCESS", "Browser simulace dokončena")
            
    except Exception as e:
        logger.log("ERROR", f"Browser automatizace selhala: {str(e)}")


# ============================================
# MAIN SIMULATION ORCHESTRATOR
# ============================================

async def main():
    """
    Hlavní orchestrátor komplexní simulace HLINIK.
    Spouští všechny fáze testu a loguje do lore-web.
    """
    logger = TestLogger("HLINIK Comprehensive Simulation - All Roles, All Phases")
    
    logger.log("INFO", "=" * 70)
    logger.log("INFO", "  🏭 HLINÍK a syn s.r.o. - KOMPLETNÍ SIMULACE SMĚNY 🏭")
    logger.log("INFO", "  IRIS 4.0 | Phase 34 | All 20 Roles | All Relationships")
    logger.log("INFO", "=" * 70)
    
    # Load data
    if not ROLES_FILE.exists():
        logger.log("ERROR", f"Roles file missing at {ROLES_FILE}")
        logger.save()
        return
        
    if not RELATIONS_FILE.exists():
        logger.log("ERROR", f"Relations file missing at {RELATIONS_FILE}")
        logger.save()
        return

    with open(ROLES_FILE, "r", encoding="utf-8") as f:
        roles = json.load(f)
    
    with open(RELATIONS_FILE, "r", encoding="utf-8") as f:
        relations = json.load(f)
    
    logger.log("INFO", f"Načteno {len(roles)} rolí a {len(relations)} vztahů")
    
    # Separate roles by type
    users = [r for r in roles if r["type"] == "user"]
    agents = [r for r in roles if r["type"] == "agent"]
    admins = [r for r in roles if r["type"] == "admin"]
    
    logger.log("INFO", f"Uživatelé: {len(users)} | Agenti: {len(agents)} | Správci: {len(admins)}")
    
    # ========================================
    # PHASE 1: Browser Simulation (UI Tests)
    # ========================================
    await run_browser_simulation(logger, roles, relations)
    
    # ========================================
    # PHASE 2: WebSocket Simulation (All roles)
    # ========================================
    logger.log_phase("WS_SIMULATION", "WebSocket simulace všech 20 rolí")
    
    logger.log("INFO", f"Spouštím {len(roles)} paralelních WebSocket připojení...")
    
    ws_tasks = []
    for role in roles:
        ws_tasks.append(simulate_user_session(role, logger, relations))
    
    if ws_tasks:
        await asyncio.gather(*ws_tasks)
    
    logger.log("SUCCESS", "WebSocket simulace dokončena")
    
    # ========================================
    # FINAL SUMMARY
    # ========================================
    logger.log_phase("SUMMARY", "Závěrečná sumarizace")
    
    stats = logger.get_stats()
    logger.log("INFO", f"📊 Celkem připojeno: {stats['total_connections']} (U:{stats['users_active']} A:{stats['agents_active']} S:{stats['admins_active']})")
    logger.log("INFO", f"⏱️ Průměrná latence: {stats['avg_latency']}ms")
    logger.log("INFO", f"💰 Ekonomické události: {stats['economy_events']}")
    logger.log("INFO", f"🔗 Vztahové interakce: {stats['relationship_events']}")
    logger.log("INFO", f"📸 Screenshoty: {stats['screenshots']}")
    
    if stats['errors'] > 0:
        logger.log("WARNING", f"⚠️ Počet chyb: {stats['errors']}")
    else:
        logger.log("SUCCESS", "✅ Žádné kritické chyby!")
    
    # Save results
    logger.save()
    
    print("\n" + "=" * 70)
    print("  ✅ HLINIK COMPREHENSIVE SIMULATION COMPLETE ✅")
    print("  Výsledky uloženy do: doc/iris/lore-web/data/test_runs/")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
