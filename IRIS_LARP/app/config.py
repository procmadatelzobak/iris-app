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
    
    def __init__(self):
        # Security Check for SECRET_KEY
        iris_env = os.getenv("IRIS_ENV", "development")
        if self.SECRET_KEY == "insecure-change-me-for-production":
            if iris_env == "production":
                raise ValueError(
                    "FATAL: Running in production with insecure default SECRET_KEY! "
                    "Set a secure SECRET_KEY environment variable."
                )
            else:
                print("\n" + "=" * 60)
                print("⚠️  WARN: Running with insecure default SECRET_KEY!")
                print("   Set SECRET_KEY env variable for production use.")
                print("=" * 60 + "\n")

settings = Settings()
