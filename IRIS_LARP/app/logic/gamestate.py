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
        self.hyper_visibility_mode = HyperVisibilityMode.NORMAL # Default
        self.chernobyl_value = settings.DEFAULT_CHERNOBYL_VALUE
        self.chernobyl_mode = ChernobylMode.NORMAL
        
        # v1.4 Power & Economy
        self.power_capacity = 100
        self.power_load = 0
        self.is_overloaded = False
        
        self.treasury_balance = 0
        self.tax_rate = 0.1 # 10%
        
        # v1.4 Timer
        self.agent_response_window = 120 # Default 2 mins (Standard)
        
        # LLM Configurations
        self.llm_config_task = LLMConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4o",
            system_prompt="You are a strict task evaluator."
        )
        self.llm_config_hyper = LLMConfig(
            provider=LLMProvider.OPENROUTER,
            model_name="google/gemini-2.0-flash-lite-preview-02-05:free",
            system_prompt="You are an AI assistant."
        )

        self.initialized = True
        
    def set_chernobyl(self, value: int):
        self.chernobyl_value = max(0, min(100, value))
        return self.chernobyl_value
        
    def report_anomaly(self):
        self.chernobyl_value = min(100, self.chernobyl_value + 5)
        return self.chernobyl_value

    def calc_load(self, active_terminals: int = 0, active_autopilots: int = 0, low_latency_active: bool = False):
        # Base: 10
        # Active Terminal: 2 * N
        # Optimizer: +5 (Assumed ON if low_latency is ON? No, spec says separate. I'll add method arg or assume usage)
        # Let's assume Optimizer is tracked elsewhere or we add a toggle.
        # For now, simplistic calc:
        base = 10
        terminals = 2 * active_terminals
        hyper = 10 * active_autopilots
        latency = 30 if low_latency_active else 0
        
        self.power_load = base + terminals + hyper + latency
        return self.power_load

    def check_overload(self):
        was_overloaded = self.is_overloaded
        self.is_overloaded = self.power_load > self.power_capacity
        return self.is_overloaded != was_overloaded # Return True if state changed

    def process_tick(self):
        # Decay logic for Chernobyl
        if self.chernobyl_mode == ChernobylMode.NORMAL:
            decay = 1
        elif self.chernobyl_mode == ChernobylMode.LOW_POWER:
            decay = 3
        else: # OVERCLOCK
            decay = 0
            
        self.chernobyl_value = max(0, self.chernobyl_value - decay)
        
        # Power calc should happen here or on event?
        # Tick is good for regular updates.
        # But we need external data (active sessions).
        # We'll rely on sockets.py to update load during its broadcast loop or similar.
        
        return self.chernobyl_value
        
    def increment_shift(self):
        self.global_shift_offset = (self.global_shift_offset + 1) % settings.TOTAL_SESSIONS
        return self.global_shift_offset

    def set_shift(self, value: int):
        self.global_shift_offset = value % settings.TOTAL_SESSIONS
        return self.global_shift_offset

gamestate = GameState()
