from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from ..dependencies import get_current_admin
from ..logic.llm_core import llm_service, LLMConfig, LLMProvider
from ..logic.gamestate import gamestate

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/llm/models/{provider}")
async def list_models(provider: LLMProvider, admin=Depends(get_current_admin)):
    return llm_service.list_models(provider)

@router.get("/llm/config")
async def get_llm_config(admin=Depends(get_current_admin)):
    return {
        "task": gamestate.llm_config_task,
        "hyper": gamestate.llm_config_hyper
    }

@router.post("/llm/config/{config_type}")
async def set_llm_config(config_type: str, config: LLMConfig, admin=Depends(get_current_admin)):
    if config_type == "task":
        gamestate.llm_config_task = config
    elif config_type == "hyper":
        gamestate.llm_config_hyper = config
    else:
        raise HTTPException(status_code=400, detail="Invalid config type")
    return {"status": "ok"}

# API Key Management
from ..database import SessionLocal, SystemConfig
from pydantic import BaseModel

class KeyUpdate(BaseModel):
    provider: LLMProvider
    key: str

@router.get("/llm/keys")
async def get_keys(admin=Depends(get_current_admin)):
    db = SessionLocal()
    keys = {}
    for provider in LLMProvider:
        key_name = f"{provider.value.upper()}_API_KEY"
        config = db.query(SystemConfig).filter(SystemConfig.key == key_name).first()
        val = config.value if config else ""
        # Mask
        if val and len(val) > 8:
            keys[provider.value] = f"{val[:4]}...{val[-4:]}"
        elif val:
            keys[provider.value] = "****"
        else:
            keys[provider.value] = None
    db.close()
    return keys

@router.post("/llm/keys")
async def set_key(update: KeyUpdate, admin=Depends(get_current_admin)):
    db = SessionLocal()
    key_name = f"{update.provider.value.upper()}_API_KEY"
    config = db.query(SystemConfig).filter(SystemConfig.key == key_name).first()
    if not config:
        config = SystemConfig(key=key_name, value=update.key)
        db.add(config)
    else:
        config.value = update.key
    db.commit()
    db.close()
    return {"status": "updated", "provider": update.provider}

# --- ECONOMY & TASKS ---
from ..database import User, Task, TaskStatus, ChatLog, UserRole
from ..logic.routing import routing_logic

class EconomyAction(BaseModel):
    user_id: int
    amount: int = 0
    reason: str = "Admin Action"

@router.get("/data/users")
async def get_users(admin=Depends(get_current_admin)):
    db = SessionLocal()
    users = db.query(User).filter(User.role == UserRole.USER).all()
    res = []
    for u in users:
        res.append({
            "id": u.id,
            "username": u.username,
            "credits": u.credits,
            "status_level": u.status_level,
            "is_locked": u.is_locked
        })
    db.close()
    return res

@router.post("/economy/fine")
async def fine_user(action: EconomyAction, admin=Depends(get_current_admin)):
    db = SessionLocal()
    user = db.query(User).filter(User.id == action.user_id).first()
    if user:
        user.credits -= action.amount
        db.commit()
        # notify user
        await routing_logic.broadcast_to_session(user.id, f'{{"type": "economy_update", "credits": {user.credits}, "msg": "FINED: {action.reason}"}}')
    db.close()
    return {"status": "ok"}

@router.post("/economy/bonus")
async def bonus_user(action: EconomyAction, admin=Depends(get_current_admin)):
    db = SessionLocal()
    user = db.query(User).filter(User.id == action.user_id).first()
    if user:
        user.credits += action.amount
        db.commit()
        await routing_logic.broadcast_to_session(user.id, f'{{"type": "economy_update", "credits": {user.credits}, "msg": "BONUS: {action.reason}"}}')
    db.close()
    return {"status": "ok"}

@router.post("/economy/toggle_lock")
async def toggle_lock(action: EconomyAction, admin=Depends(get_current_admin)):
    db = SessionLocal()
    user = db.query(User).filter(User.id == action.user_id).first()
    if user:
        user.is_locked = not user.is_locked
        db.commit()
        state = "LOCKED" if user.is_locked else "UNLOCKED"
        await routing_logic.broadcast_to_session(user.id, f'{{"type": "lock_update", "locked": {str(user.is_locked).lower()}}}')
    db.close()
    return {"status": "ok", "state": state}

@router.post("/economy/global_bonus")
async def global_bonus(action: EconomyAction, admin=Depends(get_current_admin)):
    # user_id ignored
    db = SessionLocal()
    users = db.query(User).filter(User.role == UserRole.USER).all()
    for user in users:
        user.credits += action.amount
        await routing_logic.broadcast_to_session(user.id, f'{{"type": "economy_update", "credits": {user.credits}, "msg": "GLOBAL STIMULUS: {action.reason}"}}')
    db.commit()
    db.close()
    return {"status": "ok", "count": len(users)}

@router.post("/economy/reset")
async def reset_economy(admin=Depends(get_current_admin)):
    db = SessionLocal()
    users = db.query(User).filter(User.role == UserRole.USER).all()
    for user in users:
        user.credits = 100 # Default
        user.is_locked = False
        await routing_logic.broadcast_to_session(user.id, f'{{"type": "user_status", "credits": 100, "is_locked": false}}')
    db.commit()
    db.close()
    return {"status": "reset", "count": len(users)}

# Tasks
class TaskAction(BaseModel):
    task_id: int
    reward: int = 0 # For approval
    rating: int = 0 # For payment (0-100)

@router.get("/tasks")
async def get_tasks(admin=Depends(get_current_admin)):
    db = SessionLocal()
    tasks = db.query(Task).all()
    # Simple serialization
    res = []
    for t in tasks:
        res.append({
            "id": t.id,
            "user_id": t.user_id,
            "prompt": t.prompt_desc,
            "status": t.status,
            "reward": t.reward_offered,
            "submission": t.submission_content
        })
    db.close()
    return res

@router.post("/tasks/approve")
async def approve_task(action: TaskAction, admin=Depends(get_current_admin)):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == action.task_id).first()
    if task:
        task.status = TaskStatus.ACTIVE
        task.reward_offered = action.reward
        db.commit()
        # Notify User
        await routing_logic.broadcast_to_session(task.user_id, f'{{"type": "task_update", "id": {task.id}, "status": "active", "reward": {action.reward}}}')
    db.close()
    return {"status": "approved"}

@router.post("/tasks/pay")
async def pay_task(action: TaskAction, admin=Depends(get_current_admin)):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == action.task_id).first()
    if task and task.status == TaskStatus.SUBMITTED:
        task.status = TaskStatus.COMPLETED
        task.final_rating = action.rating
        
        # Calc payout
        payout = int(task.reward_offered * (action.rating / 100))
        
        # Add credits
        user = db.query(User).filter(User.id == task.user_id).first()
        if user:
            user.credits += payout
        
        db.commit()
        
        await routing_logic.broadcast_to_session(task.user_id, f'{{"type": "economy_update", "credits": {user.credits}, "msg": "TASK COMPLETED: +{payout} CR"}}')
        await routing_logic.broadcast_to_session(task.user_id, f'{{"type": "task_update", "id": {task.id}, "status": "completed"}}')

    db.close()
    return {"status": "paid"}
