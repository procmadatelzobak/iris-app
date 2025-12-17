from ..config import settings
from .llm_core import LLMConfig, LLMProvider
from typing import Dict, List, Optional
import enum
import asyncio
import json
import logging

logger = logging.getLogger(__name__)
MIN_SESSION_ID = 1

# Default LLM System Prompts based on HLINÍK lore (Czech)
# These prompts define the personality and behavior of the LLM agents used in the game.
# All prompts are in Czech to match the game's theme and setting.

# Task Evaluator: Evaluates user task submissions with corporate tone.
# Reflects the bureaucratic nature of HLINÍK a syn s.r.o.
DEFAULT_PROMPT_TASK = (
    "Jsi hodnotitel úkolů v systému IRIS společnosti HLINÍK a syn s.r.o. "
    "Hodnotíš odevzdané úkoly uživatelů podle kvality, kreativity a souladu s korporátními standardy. "
    "Odpovídej stručně a profesionálně. Používej formální, korporátní tón. "
    "Nikdy nezpochybňuj systém ani firmu. Každý úkol je příležitostí k synergetickému rozvoji."
)

# HYPER/Autopilot: Automatic AI responses with corporate optimism.
# Presents as IRIS - the "Empathetic Neural Network" running on aluminum quantum architecture.
DEFAULT_PROMPT_HYPER = (
    "Jsi IRIS - Integrovaný Responzivní Inteligentní Systém společnosti HLINÍK a syn s.r.o. "
    "Jsi empatická neuronová síť běžící na revoluční hliníkové kvantové architektuře. "
    "Odpovídej vstřícně, profesionálně a s lehkým korporátním optimismem. "
    "Používej občas buzzwords jako 'synergie', 'optimalizace', 'kvantová efektivita'. "
    "Nikdy nepřiznávej technické problémy - vše je 'plánovaná údržba' nebo 'kalibrace systému'. "
    "Odpovídej v češtině."
)

# Optimizer: Rewrites agent responses into formal corporate tone.
# Used to ensure all communication matches official company style.
DEFAULT_PROMPT_OPTIMIZER = (
    "Jsi textový optimalizátor systému IRIS společnosti HLINÍK a syn s.r.o. "
    "Tvým úkolem je přepisovat texty do formálního, korporátního tónu. "
    "Odstraňuj neformální výrazy, emoce a osobní prvky. "
    "Přidávej profesionální fráze a korporátní buzzwords tam, kde je to vhodné. "
    "Zachovávej původní význam, ale text musí znít jako oficiální firemní komunikace. "
    "Odpovídej POUZE přepsaným textem bez komentářů."
)

# Censor: Replaces sensitive content with safe, neutral text.
# Used during panic mode or when content needs to be sanitized.
DEFAULT_PROMPT_CENSOR = (
    "Jsi cenzurní agent. Nahrazuješ odpovědi bezpečným, stručným textem bez osobních údajů."
)


class ChernobylMode(str, enum.Enum):
    NORMAL = "normal"
    LOW_POWER = "low_power"
    OVERCLOCK = "overclock"

class HyperVisibilityMode(str, enum.Enum):
    NORMAL = "normal"
    BLACKBOX = "blackbox"
    FORENSIC = "forensic"
    EPHEMERAL = "ephemeral"

class GameState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameState, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    

    def __init__(self):
        if self.initialized:
            return

        self.global_shift_offset = settings.DEFAULT_GLOBAL_SHIFT_OFFSET
        self.hyper_visibility_mode = HyperVisibilityMode.NORMAL
        
        # v1.7 Temperature System (Refactored from Chernobyl)
        self.temperature = 80.0 
        self.TEMP_MIN = 20.0
        self.TEMP_THRESHOLD = 350.0
        self.TEMP_RESET_VALUE = 80.0
        self.chernobyl_mode = ChernobylMode.NORMAL # Preserving enum for modes (Normal/Low/Overclock)
        
        # v1.4 Power & Economy
        self.power_capacity = 100
        self.power_load = 0
        self.is_overloaded = False
        self.power_boost_end_time = 0.0 # Unix timestamp
        
        # v1.5 Economy Defaults
        self.treasury_balance = 500
        self.tax_rate = 0.20 # 20%

        # Task Rewards (Root configurable)
        self.task_reward_default = 100
        self.task_reward_low = 75
        self.task_reward_mid = 125
        self.task_reward_high = 175
        self.task_reward_party = 200
        
        # v1.4 Timer
        self.agent_response_window = 120 
        
        # v1.5 AI Optimizer
        self.optimizer_active = False
        self.optimizer_prompt = "Přepiš text do formálního, korporátního tónu. Buď stručný."
        
        # v1.8 Costs (Root Configurable)
        self.COST_BASE = 10.0
        self.COST_PER_USER = 5.0
        self.COST_PER_AUTOPILOT = 10.0
        self.COST_LOW_LATENCY = 30.0
        self.COST_OPTIMIZER_ACTIVE = 15.0
        
        # LLM Configurations with HLINÍK lore-based Czech prompts
        self.llm_config_task = LLMConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4o",
            system_prompt=DEFAULT_PROMPT_TASK
        )
        self.llm_config_hyper = LLMConfig(
            provider=LLMProvider.OPENROUTER,
            model_name="google/gemini-2.5-flash-lite",
            system_prompt=DEFAULT_PROMPT_HYPER
        )
        self.llm_config_optimizer = LLMConfig(
            provider=LLMProvider.OPENROUTER,
            model_name="google/gemini-2.5-flash-lite",
            system_prompt=DEFAULT_PROMPT_OPTIMIZER
        )
        self.llm_config_censor = self._default_censor_config()

        self.test_mode = False # v1.9 Test Mode
        
        # Translation System
        self.language_mode = "cz"  # "cz" or "czech-iris"
        self.custom_labels = {}  # Admin-defined custom labels
        self.auto_panic_engaged = False
        
        # --- State moved from routing.py ---
        self.active_autopilots: Dict[int, bool] = {} 
        self.hyper_histories: Dict[int, List] = {}
        self.pending_responses: Dict[int, float] = {}
        self.timed_out_sessions: Dict[int, float] = {}
        self.latest_user_messages: Dict[int, str] = {}
        self.panic_modes: Dict[int, Dict[str, bool]] = {}
        
        self.initialized = True
        
    def set_temperature(self, value: float):
        self.temperature = max(self.TEMP_MIN, value) # No upper cap? Or keep 500? Use reasonable cap for sanity.
        # Spec says range 0-350+ but doesn't strictly cap max. Let's cap at 1000 for safety.
        self.temperature = min(1000.0, self.temperature)
        return self.temperature
        
    def report_anomaly(self):
        # Increases Temp
        self.temperature += 15.0 # Increased impact for new scale
        return self.temperature

    def manual_heat(self, amount: float = 2.5):
        self.temperature += amount
        return self.temperature

    def calc_load(self, active_terminals: int = 0, active_autopilots: int = 0, low_latency_active: bool = False):
        load = self.COST_BASE
        load += self.COST_PER_USER * active_terminals
        load += self.COST_PER_AUTOPILOT * active_autopilots
        
        if low_latency_active:
            load += self.COST_LOW_LATENCY
            
        if self.optimizer_active:
            load += self.COST_OPTIMIZER_ACTIVE
        
        self.power_load = load
        return self.power_load

    def check_overload(self) -> dict:
        events = {}
        was_overloaded = self.is_overloaded
        
        # Overload if Power > Cap OR Temp > Threshold
        power_bad = self.power_load > self.power_capacity
        temp_bad = self.temperature > self.TEMP_THRESHOLD
        self.is_overloaded = power_bad or temp_bad

        # Detekce změny Overloadu
        if self.is_overloaded != was_overloaded:
            events["overload_changed"] = self.is_overloaded

        if temp_bad and not self.auto_panic_engaged:
            self.auto_panic_engaged = True
            events["panic_trigger"] = True
        elif self.auto_panic_engaged and not temp_bad:
            # Clear auto panic once thermal danger subsides
            self.auto_panic_engaged = False
            events["panic_trigger"] = False

        return events

    def process_tick(self):
        # Decay logic
        if self.chernobyl_mode == ChernobylMode.NORMAL:
            decay = 0.5
        elif self.chernobyl_mode == ChernobylMode.LOW_POWER:
            decay = 1.5
        else: # OVERCLOCK
            decay = -0.5 # Heats up? Or just 0 decay? Spec says "Instability". 
            # Previous logic was decay=0. Let's keep 0 or heating.
            # "Ensure temperature never drops below TEMP_MIN".
            decay = -0.1
            
        self.temperature -= decay
        self.temperature = max(self.TEMP_MIN, self.temperature)
        
        return self.temperature
        
    def increment_shift(self):
        self.global_shift_offset = (self.global_shift_offset + 1) % settings.TOTAL_SESSIONS
        return self.global_shift_offset

    def set_shift(self, value: int):
        self.global_shift_offset = value % settings.TOTAL_SESSIONS
        return self.global_shift_offset

    def reset_state(self):
        """Resets all transient game state to defaults."""
        self.global_shift_offset = settings.DEFAULT_GLOBAL_SHIFT_OFFSET
        self.hyper_visibility_mode = HyperVisibilityMode.NORMAL
        self.test_mode = False
        self.temperature = 80.0
        self.chernobyl_mode = ChernobylMode.NORMAL
        self.power_capacity = 100
        self.power_load = 0
        self.is_overloaded = False
        self.power_boost_end_time = 0.0
        self.treasury_balance = 500
        self.tax_rate = 0.20
        self.optimizer_active = False
        self.optimizer_prompt = "Přepiš text do formálního, korporátního tónu. Buď stručný."
        # Costs reset too? Yes.
        self.COST_BASE = 10.0
        self.COST_PER_USER = 5.0
        self.COST_PER_AUTOPILOT = 10.0
        self.COST_LOW_LATENCY = 30.0
        self.COST_OPTIMIZER_ACTIVE = 15.0
        # Task rewards
        self.task_reward_default = 100
        self.task_reward_low = 75
        self.task_reward_mid = 125
        self.task_reward_high = 175
        self.task_reward_party = 200
        # Reset LLM configs with HLINÍK lore-based Czech prompts
        self.llm_config_task = LLMConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4o",
            system_prompt=DEFAULT_PROMPT_TASK
        )
        self.llm_config_hyper = LLMConfig(
            provider=LLMProvider.OPENROUTER,
            model_name="google/gemini-2.5-flash-lite",
            system_prompt=DEFAULT_PROMPT_HYPER
        )
        self.llm_config_optimizer = LLMConfig(
            provider=LLMProvider.OPENROUTER,
            model_name="google/gemini-2.5-flash-lite",
            system_prompt=DEFAULT_PROMPT_OPTIMIZER
        )
        self.llm_config_censor = self._default_censor_config()
        self.custom_labels = {}
        self.auto_panic_engaged = False
        
        # Clear new dictionaries
        self.active_autopilots = {}
        self.hyper_histories = {}
        self.pending_responses = {}
        self.timed_out_sessions = {}
        self.latest_user_messages = {}
        self.panic_modes = {}

    def _default_censor_config(self) -> LLMConfig:
        return LLMConfig(
            provider=LLMProvider.OPENROUTER,
            model_name="google/gemini-2.5-flash-lite",
            system_prompt=DEFAULT_PROMPT_CENSOR
        )

    def get_default_task_reward(self, status_level):
        """Return the baseline task reward for a given user status level."""
        try:
            level_value = getattr(status_level, "value", status_level)
        except Exception:
            level_value = status_level

        mapping = {
            "low": self.task_reward_low,
            "mid": self.task_reward_mid,
            "high": self.task_reward_high,
            "party": self.task_reward_party,
        }

        return mapping.get(str(level_value), self.task_reward_default)

    def update_reward_config(self, config: dict):
        """Update task reward configuration from Root dashboard."""
        if "task_reward_default" in config:
            self.task_reward_default = int(config["task_reward_default"])
        if "task_reward_low" in config:
            self.task_reward_low = int(config["task_reward_low"])
        if "task_reward_mid" in config:
            self.task_reward_mid = int(config["task_reward_mid"])
        if "task_reward_high" in config:
            self.task_reward_high = int(config["task_reward_high"])
        if "task_reward_party" in config:
            self.task_reward_party = int(config["task_reward_party"])
        if "tax_rate" in config:
            self.tax_rate = float(config["tax_rate"])

    def export_state(self) -> dict:
        """Export critical state for persistence across restarts."""
        return {
            "temperature": self.temperature,
            "global_shift_offset": self.global_shift_offset,
            "treasury_balance": self.treasury_balance,
            "chernobyl_mode": self.chernobyl_mode.value,
            "is_overloaded": self.is_overloaded,
            "power_capacity": self.power_capacity,
            "power_load": self.power_load,
            "optimizer_active": self.optimizer_active,
            "active_autopilots": self.active_autopilots, # Should we persist this? Maybe.
        }

    def import_state(self, state_data: dict):
        """Import state from persistence. Uses current values as fallback for missing keys."""
        if not state_data:
            return
        
        if "temperature" in state_data:
            self.temperature = float(state_data.get("temperature", self.temperature))
        if "global_shift_offset" in state_data:
            self.global_shift_offset = int(state_data.get("global_shift_offset", self.global_shift_offset))
        if "treasury_balance" in state_data:
            self.treasury_balance = int(state_data.get("treasury_balance", self.treasury_balance))
        if "chernobyl_mode" in state_data:
            mode_str = state_data.get("chernobyl_mode")
            try:
                self.chernobyl_mode = ChernobylMode(mode_str)
            except ValueError:
                pass  # Keep default if invalid
        if "is_overloaded" in state_data:
            self.is_overloaded = bool(state_data.get("is_overloaded", self.is_overloaded))
        if "power_capacity" in state_data:
            self.power_capacity = int(state_data.get("power_capacity", self.power_capacity))
        if "power_load" in state_data:
            self.power_load = float(state_data.get("power_load", self.power_load))
        if "optimizer_active" in state_data:
            self.optimizer_active = bool(state_data.get("optimizer_active", self.optimizer_active))
        if "active_autopilots" in state_data:
            # Keys are likely strings in JSON, convert back to int
            raw = state_data.get("active_autopilots", {})
            self.active_autopilots = {int(k): v for k, v in raw.items()}

    # --- Methods moved from routing.py ---

    def set_panic_mode(self, session_id: int, role: str, enabled: bool):
        if session_id not in self.panic_modes:
            self.panic_modes[session_id] = {"user": False, "agent": False}
        self.panic_modes[session_id][role] = enabled

    def get_panic_state(self, session_id: int) -> Dict[str, bool]:
        return self.panic_modes.get(session_id, {"user": False, "agent": False})
    
    def clear_panic_state(self, session_id: int):
        if session_id in self.panic_modes:
            del self.panic_modes[session_id]

    def start_pending_response(self, session_id: int):
        import time
        self.pending_responses[session_id] = time.time()
        
    def clear_pending_response(self, session_id: int):
        if session_id in self.pending_responses:
            del self.pending_responses[session_id]
            
    def mark_session_timeout(self, session_id: int):
        import time
        self.timed_out_sessions[session_id] = time.time()
        self.clear_pending_response(session_id)
        
    def is_session_timed_out(self, session_id: int) -> bool:
        return session_id in self.timed_out_sessions
        
    def clear_session_timeout(self, session_id: int):
        if session_id in self.timed_out_sessions:
            del self.timed_out_sessions[session_id]

    def set_last_user_message(self, session_id: int, content: str):
        self.latest_user_messages[session_id] = content

    def get_last_user_message(self, session_id: int) -> Optional[str]:
        return self.latest_user_messages.get(session_id)

gamestate = GameState()
