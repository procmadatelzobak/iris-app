from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import enum
from .config import settings

# SQLite specifics: check_same_thread=False is needed for FastAPI's threading
connect_args = {"check_same_thread": False}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Enums
class UserRole(str, enum.Enum):
    USER = "user"
    AGENT = "agent"
    ADMIN = "admin"

class StatusLevel(str, enum.Enum):
    LOW = "low"
    MID = "mid"
    HIGH = "high"

class TaskStatus(str, enum.Enum):
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    SUBMITTED = "submitted"
    COMPLETED = "completed"
    PAID = "paid"

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    credits = Column(Integer, default=100)
    status_level = Column(Enum(StatusLevel), default=StatusLevel.LOW)
    is_locked = Column(Boolean, default=False)
    
    logs = relationship("ChatLog", back_populates="sender")
    tasks = relationship("Task", back_populates="user")

class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, index=True) # Logical session ID (1-8)
    sender_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_hyper = Column(Boolean, default=False)
    is_hidden_for_agent = Column(Boolean, default=False)
    was_reported = Column(Boolean, default=False)

    sender = relationship("User", back_populates="logs")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    prompt_desc = Column(Text)
    reward_offered = Column(Integer, default=0)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING_APPROVAL)
    submission_content = Column(Text, nullable=True)
    final_rating = Column(Integer, default=0) # Percentage

    user = relationship("User", back_populates="tasks")

class SystemConfig(Base):
    __tablename__ = "system_config"

    key = Column(String, primary_key=True, index=True)
    value = Column(String) # JSON or simple string

def init_db():
    Base.metadata.create_all(bind=engine)
