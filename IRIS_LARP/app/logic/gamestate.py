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

    def process_tick(self):
        if self.chernobyl_mode == ChernobylMode.NORMAL:
            decay = 1
        elif self.chernobyl_mode == ChernobylMode.LOW_POWER:
            decay = 3
        else: # OVERCLOCK
            decay = 0
            
        self.chernobyl_value = max(0, self.chernobyl_value - decay)
        return self.chernobyl_value
        
    def increment_shift(self):
        self.global_shift_offset = (self.global_shift_offset + 1) % settings.TOTAL_SESSIONS
        return self.global_shift_offset

    def set_shift(self, value: int):
        self.global_shift_offset = value % settings.TOTAL_SESSIONS
        return self.global_shift_offset

gamestate = GameState()
