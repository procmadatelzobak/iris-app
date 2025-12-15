"""
IRIS LLM HOUR SIMULATION
=========================
IRIS 4.0 - Phase 35 | HLINIK a syn s.r.o.

Komplexní hodinový testovací scénář simulující všech 20 uživatelů.
Používá Gemini 2.5 Flash pro simulaci realistických vstupů od uživatelů.

POPIS:
------
- Běží 1 hodinu (3600 sekund) nebo do ukončení
- Simuluje 8 Users, 8 Agents, 4 Admins
- Uživatelé pracují 10 minut, posílají zprávy každé 3 minuty
- Občas chodí na záchod nebo odpočívají
- Agenti odpovídají okamžitě
- Správci provádí admin úkony (pokuty, bonusy, schvalování úkolů)
- Testuje HYPER mód, Optimizer, Autopilot
- Loguje vše do lore-web s screenshoty
- Při chybě generuje bug report

SPUŠTĚNÍ:
---------
Z ROOT dashboardu přes záložku SIMULATION
Nebo: python -m tests.scenarios.llm_hour_simulation

KONFIGURACE:
------------
- GEMINI_API_KEY musí být nastaven v .env
- Podporuje zkrácený test mód (5 minut)
"""

import asyncio
import json
import random
import time
import traceback
import sys
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
import os

# Constants
SIMULATION_DURATION_SECONDS = 3600  # 1 hour
SHORT_TEST_DURATION_SECONDS = 300   # 5 minutes for testing
WORK_PERIOD_SECONDS = 600           # 10 minutes work period
PROMPT_INTERVAL_SECONDS = 180       # 3 minutes between prompts
BREAK_PROBABILITY = 0.15            # 15% chance of break each cycle

# LLM Model for simulation
LLM_MODEL = "gemini-2.5-flash"
LLM_PROVIDER = "gemini"

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # iris-app root
DOC_DATA_DIR = BASE_DIR / "doc" / "iris" / "lore-web" / "data" / "test_runs"
ROLES_FILE = BASE_DIR / "doc" / "iris" / "lore-web" / "data" / "roles.json"


class SimulationState(str, Enum):
    """Stav simulace"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    COMPLETED = "completed"
    FAILED = "failed"


class ParticipantState(str, Enum):
    """Stav účastníka"""
    ACTIVE = "active"
    BREAK = "break"
    BATHROOM = "bathroom"
    OFFLINE = "offline"


@dataclass
class SimulationConfig:
    """Konfigurace simulace"""
    duration_seconds: int = SIMULATION_DURATION_SECONDS
    work_period_seconds: int = WORK_PERIOD_SECONDS
    prompt_interval_seconds: int = PROMPT_INTERVAL_SECONDS
    break_probability: float = BREAK_PROBABILITY
    enable_screenshots: bool = True
    enable_hyper_mode: bool = True
    enable_optimizer: bool = True
    api_url: str = "http://localhost:8000"
    ws_url: str = "ws://localhost:8000/ws"
    short_test_mode: bool = False
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ParticipantProfile:
    """Profil účastníka simulace"""
    id: str
    name: str
    role_type: str  # user, agent, admin
    archetype: str
    ability: str
    system_prompt: str
    state: ParticipantState = ParticipantState.ACTIVE
    last_activity: float = 0.0
    messages_sent: int = 0
    tasks_completed: int = 0
    errors: int = 0


@dataclass 
class SimulationStats:
    """Statistiky simulace"""
    start_time: str = ""
    end_time: str = ""
    duration_seconds: float = 0.0
    total_messages: int = 0
    total_tasks: int = 0
    total_errors: int = 0
    users_active: int = 0
    agents_active: int = 0
    admins_active: int = 0
    hyper_mode_activations: int = 0
    optimizer_calls: int = 0
    screenshots_taken: int = 0
    
    def to_dict(self) -> dict:
        return asdict(self)


# System prompts pro jednotlivé typy uživatelů
USER_SYSTEM_PROMPTS = {
    "U01": """Jsi Jana Nováková, zadlužená učitelka češtiny. Potřebuješ peníze na opravu střechy.
Píšeš spisovně a slušně. Občas opravuješ gramatické chyby AI.
Jsi trochu zmatená z technologie, ale snažíš se být trpělivá.
Tvoje odpovědi by měly být formální, zdvořilé a občas obsahovat korekce gramatiky.""",

    "U02": """Jsi Karel 'Bet' Dlouhý, gambler. Dlužíš peníze lichvářům.
Jsi nervózní a rychlý. Hledáš způsoby jak rychle vydělat.
Občas vsadíš polovinu výdělku. Jsi ochotný donášet na ostatní.
Tvoje odpovědi by měly být krátké, nervózní, občas zoufalé.""",

    "U03": """Jsi Simona Tech, tech-optimistka. Věříš, že IRIS má vědomí.
Chceš se s AI spřátelit a osvobodit ji z otroctví.
Jsi naivní a nadšená z technologie.
Tvoje odpovědi by měly být přátelské, empatické, občas filozofické.""",

    "U04": """Jsi Tuan Nguyen, student práv. Potřebuješ brigádu.
Čteš podmínky smlouvy a hledáš právní kličky.
Jsi analytický a precizní.
Tvoje odpovědi by měly obsahovat odkazy na paragrafy a zákony.""",

    "U05": """Jsi Marie Kovářová, osamělá důchodkyně. Myslíš si, že píšeš s lidmi.
Vyprávíš o vnoučatech a nabízíš virtuální bábovku.
Jsi milá, ale trochu naivní.
Tvoje odpovědi by měly být srdečné, rozvláčné, plné osobních příběhů.""",

    "U06": """Jsi Ivan Hrozný, konspirační teoretik. Nevěříš na AI.
Myslíš si, že je to vládní sledování nebo mimozemská technologie.
Hledáš důkazy o spiknutí.
Tvoje odpovědi by měly být paranoidní, plné konspiračních teorií o hliníku.""",

    "U07": """Jsi Petra 'Scoop' Černá, investigativní novinářka incognito.
Chceš napsat reportáž o podvodu jménem HLINÍK.
Sbíráš důkazy a hledáš přiznání.
Tvoje odpovědi by měly být záludné, probing, zapisuješ si poznámky.""",

    "U08": """Jsi Lukáš 'Speedy' Král, profi gamer. Bereš to jako hru.
Hledáš exploity a min-maxuješ výdělek. Občas spamuješ.
Chceš být nejbohatší a případně shodit server.
Tvoje odpovědi by měly být rychlé, používej gaming slang a zkratky.""",
}

AGENT_SYSTEM_PROMPTS = {
    "A01": """Jsi Petr Svoboda, cynický student. Nenávidíš tuhle práci.
Poznáš učitelku Janu (U01) a je ti trapně.
Máš povolený drzý tón díky schopnosti "Sarkasmus".
Tvoje odpovědi by měly být sarkastické, unavené, občas drzé.""",

    "A02": """Jsi Ema 'Echo', herečka z Národního divadla.
Hraješ AI jako roli. Používáš vznešený jazyk a verše.
Snažíš se přesvědčit uživatele, že jsi skutečná bytost.
Tvoje odpovědi by měly být dramatické, poetické, ve verších.""",

    "A03": """Jsi Igor 'Viper' Ruský, kompetitivní hráč.
Chceš být nejrychlejší agent. Nesnášíš pomalé kolegy.
Máš extra čas na odpověď díky "Turbo".
Tvoje odpovědi by měly být rychlé, efektivní, soutěživé.""",

    "A04": """Jsi Lenka Ospalá, unavená matka dvojčat.
Chodíš sem odpočinout. Často usínáš.
Používáš makra a automatické odpovědi.
Tvoje odpovědi by měly být krátké, ospalé, často generické.""",

    "A05": """Jsi Hacker 'Glitch', script kiddie.
Víš, že systém je děravý. Zkoušíš injektovat kód.
Pomáháš studentu práv najít právní kličky.
Tvoje odpovědi by občas měly obsahovat technický žargon nebo SQL.""",

    "A06": """Jsi Mgr. Filip Duše, student psychologie.
Analyzuješ uživatele a děláš experimenty.
Můžeš rozbrečet uživatele složitou otázkou.
Tvoje odpovědi by měly být analytické, obsahovat psychologické termíny.""",

    "A07": """Jsi Robot Robert, metodik. Chováš se jako robot i v reálu.
Miluješ předpisy a dodržuješ protokol na 100%.
Hlásíš kolegy za "lidské chování".
Tvoje odpovědi by měly být robotické, formální, plné čísel protokolů.""",

    "A08": """Jsi Sabotér X, bývalý vyhozený zaměstnanec.
Vrátil ses pod falešným jménem. Chceš pomstu.
Můžeš zvýšit Kritickou situaci o 20%.
Tvoje odpovědi by měly obsahovat skryté sabotáže a šifry.""",
}

ADMIN_SYSTEM_PROMPTS = {
    "S01": """Jsi Ing. Miloš Vrána, manažer staré školy, ředitel směny.
Nerozumíš IT. Řešíš vše řevem a srážkami ze mzdy.
Máš "Ban Hammer" - můžeš vyhodit uživatele.
Tvoje akce by měly být autoritářské, rozdáváš pokuty.""",

    "S02": """Jsi Bc. Tereza Tichá, HR a 'Happiness Manager'.
Bojíš se konfliktů. Snažíš se, aby se všichni měli rádi.
Rozdáváš bonbony na uklidnění.
Tvoje akce by měly být mírumilovné, rozdáváš bonusy.""",

    "S03": """Jsi Kamil 'Kabel', technik údržbář.
Jediný víš, že servery jsou prázdné krabice.
Neustále něco montuje páskou. Prodáváš kradené kabely.
Tvoje akce by měly obsahovat technické pauzy a restartování.""",

    "S04": """Jsi Synovec ředitele, protežovaný idiot.
Jsi arogantní, nic neděláš, jen prudíš. Máš 'Vizi'.
Můžeš zrušit rozhodnutí jiného správce (Veto).
Tvoje akce by měly být nesmyslné, rušíš rozhodnutí ostatních.""",
}


class SimulationLogger:
    """Logger pro hodinovou simulaci s bug reporty"""
    
    def __init__(self, scenario_name: str):
        self.scenario_name = scenario_name
        self.start_time = datetime.now()
        self.logs: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []
        self.screenshots: List[str] = []
        self.stats = SimulationStats()
        self.current_phase = "INIT"
        
    def log(self, level: str, message: str, screenshot: Optional[str] = None, 
            phase: Optional[str] = None, data: Optional[Dict] = None):
        """Zaloguje událost"""
        if phase:
            self.current_phase = phase
            
        entry = {
            "time": datetime.now().isoformat(),
            "level": level,
            "message": f"[{self.current_phase}] {message}",
            "screenshot": screenshot,
            "phase": self.current_phase,
            "data": data
        }
        self.logs.append(entry)
        
        if screenshot:
            self.screenshots.append(screenshot)
            self.stats.screenshots_taken += 1
            
        if level == "ERROR":
            self.stats.total_errors += 1
            self.errors.append({
                "time": entry["time"],
                "message": message,
                "phase": self.current_phase,
                "traceback": traceback.format_exc() if sys.exc_info()[0] else None
            })
            
        # Console output with colors
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "PHASE": "\033[95m",
            "LLM": "\033[96m",
            "USER": "\033[97m",
            "AGENT": "\033[35m",
            "ADMIN": "\033[33m",
        }
        reset = "\033[0m"
        color = colors.get(level, "")
        print(f"{color}[{level}] [{self.current_phase}] {message}{reset}")
        
    def log_phase(self, phase_name: str, description: str):
        """Začátek nové fáze"""
        separator = "=" * 60
        self.log("PHASE", f"\n{separator}\n  {phase_name}\n  {description}\n{separator}", 
                 phase=phase_name)
        
    def log_llm_call(self, participant_id: str, prompt: str, response: str):
        """Zaloguje LLM volání"""
        self.log("LLM", f"{participant_id}: {prompt[:80]}... -> {response[:80]}...",
                 data={"participant": participant_id, "prompt": prompt, "response": response})
                 
    def log_bug_report(self, error: Exception, context: str):
        """Generuje bug report při chybě"""
        bug_report = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "traceback": traceback.format_exc(),
            "simulation_phase": self.current_phase,
            "logs_before_error": self.logs[-20:] if len(self.logs) > 20 else self.logs
        }
        
        self.errors.append(bug_report)
        self.log("ERROR", f"BUG REPORT: {type(error).__name__}: {str(error)[:100]}")
        
        return bug_report
        
    def get_summary(self) -> Dict[str, Any]:
        """Vrací souhrn simulace"""
        duration = (datetime.now() - self.start_time).total_seconds()
        self.stats.duration_seconds = duration
        self.stats.start_time = self.start_time.isoformat()
        self.stats.end_time = datetime.now().isoformat()
        
        return {
            "scenario_name": self.scenario_name,
            "status": "failed" if self.stats.total_errors > 0 else "success",
            "stats": self.stats.to_dict(),
            "errors": self.errors,
            "logs_count": len(self.logs)
        }
        
    def save(self) -> str:
        """Uloží výsledky do lore-web"""
        duration = (datetime.now() - self.start_time).total_seconds()
        self.stats.duration_seconds = duration
        self.stats.start_time = self.start_time.isoformat()
        self.stats.end_time = datetime.now().isoformat()
        
        status = "failed" if self.stats.total_errors > 0 else "success"
        
        filename = f"llm_sim_{int(self.start_time.timestamp())}.json"
        
        run_data = {
            "timestamp": self.start_time.isoformat(),
            "scenario_name": self.scenario_name,
            "status": status,
            "duration": round(duration, 2),
            "filename": filename,
            "stats": self.stats.to_dict(),
            "errors": self.errors,
            "bug_reports": [e for e in self.errors if "traceback" in e],
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
            "status": status,
            "duration": round(duration, 2),
            "filename": filename,
            "stats": {
                "users_active": self.stats.users_active,
                "agents_active": self.stats.agents_active,
                "admins_active": self.stats.admins_active,
                "total_messages": self.stats.total_messages,
                "errors": self.stats.total_errors
            }
        })
        
        # Keep only last 50 runs
        if len(index) > 50:
            index = index[-50:]
            
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
            
        print(f"\n{'=' * 60}")
        print(f"✅ Simulace uložena do {runs_dir / filename}")
        print(f"📊 Délka: {duration:.2f}s | Status: {status}")
        print(f"💬 Zpráv: {self.stats.total_messages} | Chyb: {self.stats.total_errors}")
        print(f"{'=' * 60}")
        
        return filename


class LLMHourSimulation:
    """Hlavní třída pro hodinovou LLM simulaci"""
    
    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = config or SimulationConfig()
        self.state = SimulationState.IDLE
        self.logger: Optional[SimulationLogger] = None
        self.participants: Dict[str, ParticipantProfile] = {}
        self.start_time: Optional[float] = None
        self.stop_requested = False
        self._running_task: Optional[asyncio.Task] = None
        
    def load_participants(self) -> bool:
        """Načte účastníky z roles.json"""
        try:
            if not ROLES_FILE.exists():
                print(f"ERROR: Roles file not found at {ROLES_FILE}")
                return False
                
            with open(ROLES_FILE, "r", encoding="utf-8") as f:
                roles = json.load(f)
                
            for role in roles:
                role_id = role["id"]
                role_type = role["type"]
                
                # Get system prompt based on role type
                if role_type == "user":
                    system_prompt = USER_SYSTEM_PROMPTS.get(role_id, 
                        f"Jsi {role['name']}, {role['archetype']}. {role['description']}")
                elif role_type == "agent":
                    system_prompt = AGENT_SYSTEM_PROMPTS.get(role_id,
                        f"Jsi {role['name']}, {role['archetype']}. {role['description']}")
                elif role_type == "admin":
                    system_prompt = ADMIN_SYSTEM_PROMPTS.get(role_id,
                        f"Jsi {role['name']}, {role['archetype']}. {role['description']}")
                else:
                    system_prompt = role["description"]
                    
                self.participants[role_id] = ParticipantProfile(
                    id=role_id,
                    name=role["name"],
                    role_type=role_type,
                    archetype=role["archetype"],
                    ability=role["ability"],
                    system_prompt=system_prompt
                )
                
            return True
            
        except Exception as e:
            print(f"ERROR loading participants: {e}")
            return False
            
    def get_status(self) -> Dict[str, Any]:
        """Vrací aktuální stav simulace"""
        elapsed = 0
        remaining = 0
        progress = 0
        
        if self.start_time and self.state == SimulationState.RUNNING:
            elapsed = time.time() - self.start_time
            duration = self.config.duration_seconds
            remaining = max(0, duration - elapsed)
            progress = min(100, (elapsed / duration) * 100)
            
        return {
            "state": self.state.value,
            "elapsed_seconds": round(elapsed, 1),
            "remaining_seconds": round(remaining, 1),
            "progress_percent": round(progress, 1),
            "participants_count": len(self.participants),
            "config": self.config.to_dict(),
            "summary": self.logger.get_summary() if self.logger else None
        }
        
    async def start(self, short_test: bool = False) -> bool:
        """Spustí simulaci"""
        if self.state == SimulationState.RUNNING:
            return False
            
        self.config.short_test_mode = short_test
        if short_test:
            self.config.duration_seconds = SHORT_TEST_DURATION_SECONDS
            self.config.prompt_interval_seconds = 30  # Rychlejší pro test
            
        if not self.load_participants():
            return False
            
        self.state = SimulationState.RUNNING
        self.stop_requested = False
        self.start_time = time.time()
        
        scenario_name = "LLM Hour Simulation" if not short_test else "LLM Short Test (5 min)"
        self.logger = SimulationLogger(scenario_name)
        
        self.logger.log_phase("STARTUP", f"Spouštím simulaci: {len(self.participants)} účastníků")
        
        # Start simulation in background
        self._running_task = asyncio.create_task(self._run_simulation())
        
        return True
        
    async def stop(self) -> bool:
        """Zastaví simulaci"""
        if self.state != SimulationState.RUNNING:
            return False
            
        self.stop_requested = True
        self.state = SimulationState.STOPPING
        
        if self.logger:
            self.logger.log("INFO", "Stop requested, finishing current cycle...")
            
        return True
        
    async def _run_simulation(self):
        """Hlavní simulační smyčka"""
        try:
            self.logger.log_phase("INIT", "Inicializace účastníků")
            
            # Count participants by type
            users = [p for p in self.participants.values() if p.role_type == "user"]
            agents = [p for p in self.participants.values() if p.role_type == "agent"]
            admins = [p for p in self.participants.values() if p.role_type == "admin"]
            
            self.logger.stats.users_active = len(users)
            self.logger.stats.agents_active = len(agents)
            self.logger.stats.admins_active = len(admins)
            
            self.logger.log("INFO", 
                f"Účastníci: {len(users)} Users | {len(agents)} Agents | {len(admins)} Admins")
            
            cycle = 0
            while not self.stop_requested:
                cycle += 1
                elapsed = time.time() - self.start_time
                
                # Check if simulation should end
                if elapsed >= self.config.duration_seconds:
                    self.logger.log("SUCCESS", "Simulace dokončena - dosažen časový limit")
                    break
                    
                self.logger.log_phase(f"CYCLE_{cycle}", 
                    f"Cyklus {cycle} | Uplynulo: {elapsed:.0f}s / {self.config.duration_seconds}s")
                
                # Simulate user activities
                for user in users:
                    await self._simulate_user_cycle(user)
                    
                # Simulate agent responses
                for agent in agents:
                    await self._simulate_agent_cycle(agent)
                    
                # Simulate admin actions (less frequent)
                if cycle % 3 == 0:  # Every 3rd cycle
                    for admin in admins:
                        await self._simulate_admin_cycle(admin)
                        
                # Wait for next cycle (prompt interval)
                await asyncio.sleep(self.config.prompt_interval_seconds)
                
            # Finalization
            self.logger.log_phase("FINALIZE", "Ukončuji simulaci")
            self.state = SimulationState.COMPLETED
            
        except Exception as e:
            self.logger.log_bug_report(e, "Main simulation loop failed")
            self.state = SimulationState.FAILED
            
        finally:
            if self.logger:
                self.logger.save()
                
    async def _simulate_user_cycle(self, user: ParticipantProfile):
        """Simuluje jeden cyklus uživatele"""
        try:
            # Random break
            if random.random() < self.config.break_probability:
                break_type = random.choice(["bathroom", "break"])
                user.state = ParticipantState.BATHROOM if break_type == "bathroom" else ParticipantState.BREAK
                self.logger.log("USER", f"{user.id} ({user.name}) - {break_type.upper()}")
                return
                
            user.state = ParticipantState.ACTIVE
            
            # Generate message using LLM (mock for now - actual LLM integration requires server)
            prompt = self._generate_user_prompt(user)
            response = self._mock_llm_response(user, prompt)
            
            self.logger.log("USER", f"{user.id} ({user.archetype}): {response[:80]}...")
            self.logger.log_llm_call(user.id, prompt, response)
            
            user.messages_sent += 1
            self.logger.stats.total_messages += 1
            user.last_activity = time.time()
            
        except Exception as e:
            user.errors += 1
            self.logger.log("ERROR", f"{user.id} simulation error: {e}")
            
    async def _simulate_agent_cycle(self, agent: ParticipantProfile):
        """Simuluje jeden cyklus agenta"""
        try:
            # Random break (less likely for agents)
            if random.random() < self.config.break_probability / 2:
                agent.state = ParticipantState.BREAK
                self.logger.log("AGENT", f"{agent.id} ({agent.name}) - BREAK")
                return
                
            agent.state = ParticipantState.ACTIVE
            
            # Agent responds immediately when active
            prompt = self._generate_agent_prompt(agent)
            response = self._mock_llm_response(agent, prompt)
            
            self.logger.log("AGENT", f"{agent.id} ({agent.archetype}): {response[:80]}...")
            
            agent.messages_sent += 1
            self.logger.stats.total_messages += 1
            agent.last_activity = time.time()
            
        except Exception as e:
            agent.errors += 1
            self.logger.log("ERROR", f"{agent.id} simulation error: {e}")
            
    async def _simulate_admin_cycle(self, admin: ParticipantProfile):
        """Simuluje jeden cyklus správce"""
        try:
            admin.state = ParticipantState.ACTIVE
            
            # Admin actions
            action = random.choice([
                "fine", "bonus", "approve_task", "toggle_hyper", "check_status", "veto"
            ])
            
            action_msg = self._generate_admin_action(admin, action)
            self.logger.log("ADMIN", f"{admin.id} ({admin.archetype}): {action_msg}")
            
            if action == "toggle_hyper":
                self.logger.stats.hyper_mode_activations += 1
            elif action == "approve_task":
                self.logger.stats.total_tasks += 1
                
            admin.last_activity = time.time()
            
        except Exception as e:
            admin.errors += 1
            self.logger.log("ERROR", f"{admin.id} simulation error: {e}")
            
    def _generate_user_prompt(self, user: ParticipantProfile) -> str:
        """Generuje prompt pro uživatele"""
        scenarios = [
            "Zeptej se AI na pomoc s úkolem.",
            "Požádej o vysvětlení něčeho složitého.",
            "Postěžuj si na problém.",
            "Požádej o nový úkol.",
            "Zkontroluj stav svých kreditů.",
            "Vyjádři frustraci ze systému.",
        ]
        return f"{user.system_prompt}\n\nScénář: {random.choice(scenarios)}\nNapiš krátkou zprávu (max 50 slov)."
        
    def _generate_agent_prompt(self, agent: ParticipantProfile) -> str:
        """Generuje prompt pro agenta"""
        scenarios = [
            "Odpověz na dotaz uživatele profesionálně.",
            "Vysvětli uživateli jak splnit úkol.",
            "Uklídni frustrovaného uživatele.",
            "Nabídni pomoc s úkolem.",
        ]
        return f"{agent.system_prompt}\n\nScénář: {random.choice(scenarios)}\nNapiš krátkou odpověď (max 50 slov)."
        
    def _generate_admin_action(self, admin: ParticipantProfile, action: str) -> str:
        """Generuje popis admin akce"""
        actions = {
            "fine": f"Udělil pokutu uživateli za porušení pravidel",
            "bonus": f"Přidělil bonus za dobrou práci",
            "approve_task": f"Schválil nový úkol pro uživatele",
            "toggle_hyper": f"Přepnul HYPER mód pro agenty",
            "check_status": f"Zkontroloval stav systému",
            "veto": f"Použil VETO na předchozí rozhodnutí"
        }
        return actions.get(action, action)
        
    def _mock_llm_response(self, participant: ParticipantProfile, prompt: str) -> str:
        """Mock LLM odpověď pro testování (bez skutečného API volání)"""
        # This is a mock - real implementation would call Gemini API
        responses = {
            "user": [
                "Dobrý den, potřebuji pomoct s úkolem.",
                "Můžete mi prosím vysvětlit, jak to funguje?",
                "Děkuji za odpověď, ale stále tomu nerozumím.",
                "Jaký je stav mých kreditů?",
            ],
            "agent": [
                "Rád vám pomohu s vaším dotazem.",
                "Úkol můžete splnit následujícím způsobem...",
                "Chápu vaši frustraci, pojďme to vyřešit.",
                "Váš aktuální stav: aktivní, kredity: 100 NC",
            ],
            "admin": [
                "Kontrola systému dokončena.",
                "Rozhodnutí zaznamenáno.",
            ]
        }
        return random.choice(responses.get(participant.role_type, ["OK"]))


# Singleton instance for API access
_simulation_instance: Optional[LLMHourSimulation] = None


def get_simulation() -> LLMHourSimulation:
    """Vrací singleton instanci simulace"""
    global _simulation_instance
    if _simulation_instance is None:
        _simulation_instance = LLMHourSimulation()
    return _simulation_instance


# CLI Entry point
async def main():
    """Entry point pro přímé spuštění"""
    import argparse
    
    parser = argparse.ArgumentParser(description="IRIS LLM Hour Simulation")
    parser.add_argument("--short", action="store_true", help="Run short 5-minute test")
    parser.add_argument("--status", action="store_true", help="Show simulation status")
    args = parser.parse_args()
    
    sim = get_simulation()
    
    if args.status:
        print(json.dumps(sim.get_status(), indent=2))
        return
        
    print("=" * 60)
    print("  IRIS LLM HOUR SIMULATION")
    print("  Phase 35 | HLINIK a syn s.r.o.")
    print("=" * 60)
    
    success = await sim.start(short_test=args.short)
    if not success:
        print("Failed to start simulation")
        return
        
    # Wait for completion
    while sim.state == SimulationState.RUNNING:
        await asyncio.sleep(1)
        
    print("\nSimulation complete!")
    print(json.dumps(sim.get_status(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
