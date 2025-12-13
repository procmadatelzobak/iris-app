import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "IRIS System"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/iris.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "insecure-change-me-for-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # System Defaults
    DEFAULT_GLOBAL_SHIFT_OFFSET: int = 0
    DEFAULT_HYPER_VISIBILITY: str = "transparent" # transparent, ephemeral, blackbox, forensic
    DEFAULT_CHERNOBYL_VALUE: int = 0
    
    # Game Logic
    TOTAL_SESSIONS: int = 8

settings = Settings()
