from ..config import settings
from .llm_core import LLMConfig, LLMProvider
import enum

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
        
        # LLM Configurations
        self.llm_config_task = LLMConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4o",
            system_prompt="You are a strict task evaluator."
        )
        self.llm_config_hyper = LLMConfig(
            provider=LLMProvider.OPENROUTER,
            model_name="google/gemini-2.5-flash-lite",
            system_prompt="You are an AI assistant."
        )
        self.llm_config_optimizer = LLMConfig(
            provider=LLMProvider.OPENROUTER,
            model_name="google/gemini-2.5-flash-lite",
            system_prompt="You are a precise rewriter. Follow all instructions."
        )

        self.test_mode = False # v1.9 Test Mode
        
        # Translation System
        self.language_mode = "cz"  # "cz" or "czech-iris"
        self.custom_labels = {}  # Admin-defined custom labels
        
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

    def check_overload(self):
        was_overloaded = self.is_overloaded
        # Overload if Power > Cap OR Temp > Threshold
        power_bad = self.power_load > self.power_capacity
        temp_bad = self.temperature > self.TEMP_THRESHOLD
        self.is_overloaded = power_bad or temp_bad
        return self.is_overloaded != was_overloaded

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
        # Reset LLM configs
        self.llm_config_task = LLMConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4o",
            system_prompt="You are a strict task evaluator."
        )
        self.llm_config_hyper = LLMConfig(
            provider=LLMProvider.OPENROUTER,
            model_name="google/gemini-2.5-flash-lite",
            system_prompt="You are an AI assistant."
        )
        self.llm_config_optimizer = LLMConfig(
            provider=LLMProvider.OPENROUTER,
            model_name="google/gemini-2.5-flash-lite",
            system_prompt="You are a precise rewriter. Follow all instructions."
        )
        # Reset custom labels (translation overrides)
        self.custom_labels = {}

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
        }

    def import_state(self, state_data: dict):
        """Import state from persistence. Uses current values as fallback for missing keys."""
        if not state_data:
            return
        
        if "temperature" in state_data:
            self.temperature = float(state_data["temperature"])
        if "global_shift_offset" in state_data:
            self.global_shift_offset = int(state_data["global_shift_offset"])
        if "treasury_balance" in state_data:
            self.treasury_balance = int(state_data["treasury_balance"])
        if "chernobyl_mode" in state_data:
            mode_str = state_data["chernobyl_mode"]
            try:
                self.chernobyl_mode = ChernobylMode(mode_str)
            except ValueError:
                pass  # Keep default if invalid
        if "is_overloaded" in state_data:
            self.is_overloaded = bool(state_data["is_overloaded"])
        if "power_capacity" in state_data:
            self.power_capacity = int(state_data["power_capacity"])

gamestate = GameState()
