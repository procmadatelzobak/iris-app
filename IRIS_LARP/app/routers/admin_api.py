from fastapi import APIRouter, Depends, HTTPException, Body

from typing import List, Dict, Optional
import json

from typing import List, Dict
from pydantic import BaseModel

from ..dependencies import get_current_admin, get_current_root
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
        "hyper": gamestate.llm_config_hyper,
        "optimizer": {
            **gamestate.llm_config_optimizer.dict(),
            "prompt": gamestate.optimizer_prompt
        },
        "censor": gamestate.llm_config_censor
    }

class OptimizerConfigPayload(BaseModel):
    provider: LLMProvider
    model_name: str
    system_prompt: str
    prompt: str

@router.post("/llm/config/{config_type}")
async def set_llm_config(config_type: str, payload: dict = Body(...), admin=Depends(get_current_admin)):
    if config_type == "task":
        gamestate.llm_config_task = LLMConfig(**payload)
    elif config_type == "hyper":
        gamestate.llm_config_hyper = LLMConfig(**payload)
    elif config_type == "optimizer":
        parsed = OptimizerConfigPayload(**payload)
        gamestate.llm_config_optimizer = LLMConfig(
            provider=parsed.provider,
            model_name=parsed.model_name,
            system_prompt=parsed.system_prompt
        )
        gamestate.optimizer_prompt = parsed.prompt
    elif config_type == "censor":
        gamestate.llm_config_censor = LLMConfig(**payload)
    else:
        raise HTTPException(status_code=400, detail="Invalid config type")
    return {"status": "ok", "config_type": config_type}

# API Key Management
from ..database import SessionLocal, SystemConfig

class KeyUpdate(BaseModel):
    provider: LLMProvider
    key: str

@router.get("/llm/keys")
async def get_keys(admin=Depends(get_current_root)):
    # Read from Settings (Env) only
    from ..config import settings
    keys = {}
    for provider in LLMProvider:
        key_name = f"{provider.value.upper()}_API_KEY"
        val = getattr(settings, key_name, "")
        
        # Mask
        if val and len(val) > 8:
            keys[provider.value] = f"{val[:4]}...{val[-4:]}"
        elif val:
            keys[provider.value] = "****"
        else:
            keys[provider.value] = None
    return keys

@router.post("/llm/keys")
async def set_key(update: KeyUpdate, admin=Depends(get_current_root)):
    raise HTTPException(
        status_code=403, 
        detail="API Key management via API is disabled for security. Please update the .env file directly and restart the server."
    )

# --- ECONOMY & TASKS ---
from ..database import User, Task, TaskStatus, ChatLog, UserRole, SystemLog, StatusLevel
from ..logic.routing import routing_logic

class PanicToggle(BaseModel):
    session_id: int
    target: str  # "user" or "agent"
    enabled: bool

@router.get("/panic/state/{session_id}")
async def get_panic_state(session_id: int, admin=Depends(get_current_admin)):
    return routing_logic.get_panic_state(session_id)

@router.post("/panic/toggle")
async def set_panic(toggle: PanicToggle, admin=Depends(get_current_admin)):
    if toggle.target not in ["user", "agent"]:
        raise HTTPException(status_code=400, detail="target must be 'user' or 'agent'")
    routing_logic.set_panic_mode(toggle.session_id, toggle.target, toggle.enabled)
    return {"status": "ok", "state": routing_logic.get_panic_state(toggle.session_id)}

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
        # Auto-lock if negative
        if user.credits < 0 and not user.is_locked:
            user.is_locked = True
            await routing_logic.broadcast_to_session(user.id, f'{{"type": "lock_update", "locked": true}}')
            
        db.commit()
        # notify user
        await routing_logic.broadcast_to_session(user.id, f'{{"type": "economy_update", "credits": {user.credits}, "msg": "FINED: {action.reason}", "is_locked": {str(user.is_locked).lower()}}}')
    db.close()
    return {"status": "ok"}

@router.post("/economy/bonus")
async def bonus_user(action: EconomyAction, admin=Depends(get_current_admin)):
    db = SessionLocal()
    user = db.query(User).filter(User.id == action.user_id).first()
    if user:
        user.credits += action.amount
        
        # Auto-lock if negative
        if user.credits < 0 and not user.is_locked:
            user.is_locked = True
            await routing_logic.broadcast_to_session(user.id, f'{{"type": "lock_update", "locked": true}}')
        
        # Auto-unlock if positive
        elif user.credits >= 0 and user.is_locked:
            user.is_locked = False
            await routing_logic.broadcast_to_session(user.id, f'{{"type": "lock_update", "locked": false}}')
            
        db.commit()
        await routing_logic.broadcast_to_session(user.id, f'{{"type": "economy_update", "credits": {user.credits}, "msg": "BONUS: {action.reason}", "is_locked": {str(user.is_locked).lower()}}}')
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
    db.close()
    return {"status": "ok", "state": state}

class StatusUpdate(BaseModel):
    user_id: int
    status: str

@router.post("/economy/set_status")
async def set_user_status(action: StatusUpdate, admin=Depends(get_current_admin)):
    db = SessionLocal()
    user = db.query(User).filter(User.id == action.user_id).first()
    if user:
        # Validate status enum? Python Enum helps but string is passed.
        # Accept low, mid, high, party
        valid = ["low", "mid", "high", "party"]
        if action.status not in valid:
             db.close()
             raise HTTPException(status_code=400, detail="Invalid status")
             
        user.status_level = action.status
        db.commit()
        
        # Broadcast theme update to User
        await routing_logic.broadcast_to_session(user.id, f'{{"type": "theme_update", "theme": "{action.status}"}}')
        
    db.close()
    return {"status": "ok", "new_level": action.status}

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
    reward: Optional[int] = None # For approval
    rating: int = 0 # For payment (0-200)
    prompt_content: str = None # v2.0 Task Editing

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
            "status": t.status.value if hasattr(t.status, "value") else str(t.status),
            "reward": t.reward_offered,
            "submission": t.submission_content,
            "rating": t.final_rating
        })
    db.close()
    return res

@router.post("/tasks/approve")
async def approve_task(action: TaskAction, admin=Depends(get_current_admin)):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == action.task_id).first()
    if not task:
        db.close()
        raise HTTPException(status_code=404, detail="Task not found")
    
    user = task.user
    
    # Calculate reward based on user status level
    reward_value = action.reward if action.reward is not None else None
    if reward_value is None or reward_value <= 0:
        level = user.status_level if user and user.status_level else StatusLevel.LOW
        reward_value = gamestate.get_default_task_reward(level)
    
    # Generate task description via LLM if not provided
    prompt_content = action.prompt_content
    if not prompt_content or prompt_content.strip() == "" or prompt_content == "Waiting for assignment...":
        from ..logic.llm_core import llm_service
        user_profile = {
            "username": user.username if user else "unknown",
            "status_level": user.status_level.value if user and user.status_level else "low",
            "credits": user.credits if user else 0
        }
        try:
            prompt_content = await llm_service.generate_task_description(user_profile)
        except Exception as e:
            print(f"LLM task generation failed: {e}")
            prompt_content = "Proveďte analýzu aktuálního stavu systému a navrhněte zlepšení."
    
    task.status = TaskStatus.ACTIVE
    task.reward_offered = reward_value
    task.prompt_desc = prompt_content
    
    db.commit()
    
    # Log
    db_log = SessionLocal()
    db_log.add(SystemLog(event_type="TASK", message=f"Task #{task.id} approved for {user.username if user else 'unknown'}, reward: {reward_value}"))
    db_log.commit()
    db_log.close()
    
    # Notify User
    await routing_logic.broadcast_to_session(
        task.user_id,
        json.dumps({
            "type": "task_update",
            "id": task.id,
            "task_id": task.id,
            "status": "active",
            "reward": task.reward_offered,
            "prompt": task.prompt_desc,
            "description": task.prompt_desc
        })
    )
    db.close()
    return {"status": "approved", "task_id": task.id, "reward": reward_value}

class GradeAction(BaseModel):
    task_id: int
    rating_modifier: float  # 0.0, 0.5, 1.0, 2.0

@router.post("/tasks/grade")
async def grade_task(action: GradeAction, admin=Depends(get_current_admin)):
    """Grade a submitted task with rating modifier (0.0, 0.5, 1.0, 2.0)"""
    allowed_modifiers = {0.0, 0.5, 1.0, 2.0}
    modifier = action.rating_modifier if action.rating_modifier in allowed_modifiers else 1.0
    
    # Convert modifier to percentage for existing economy logic
    rating_percent = int(modifier * 100)
    
    from ..logic.economy import process_task_payment
    result = process_task_payment(action.task_id, rating_percent)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Get task for logging
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == action.task_id).first()
    user = task.user if task else None
    
    # Log to SystemLog
    db.add(SystemLog(
        event_type="ECONOMY", 
        message=f"Task #{action.task_id} graded at {rating_percent}%. User {user.username if user else 'unknown'} received {result.get('net_reward', 0)} credits. Tax: {result.get('tax_collected', 0)}"
    ))
    
    # Create ChatLog entry for user
    if user:
        from ..database import ChatLog
        task_name = task.prompt_desc[:50] if task and task.prompt_desc else "Úkol"
        db.add(ChatLog(
            session_id=user.id,
            sender_id=user.id,
            content=f"📋 Úkol '{task_name}...' vyhodnocen. Odměna: {result.get('net_reward', 0)} kreditů ({rating_percent}%)."
        ))
    
    db.commit()
    db.close()
    
    # Broadcast to user
    await routing_logic.broadcast_to_session(result.get("user_id", action.task_id), json.dumps({
        "type": "task_update",
        "task_id": action.task_id,
        "status": "paid",
        "payout": result.get("actual_reward"),
        "net_reward": result.get("net_reward"),
        "rating": rating_percent
    }))
    
    # Also send economy update
    await routing_logic.broadcast_to_session(result.get("user_id", action.task_id), json.dumps({
        "type": "economy_update",
        "credits": result.get("net_reward", 0),
        "msg": f"Odměna za úkol: +{result.get('net_reward', 0)} CR"
    }))
    
    await routing_logic.broadcast_to_admins(json.dumps({"type": "admin_refresh_tasks"}))
    return result

@router.post("/tasks/pay")
async def pay_task(action: TaskAction, admin=Depends(get_current_admin)):
    from ..logic.economy import process_task_payment
    allowed = {0, 50, 100, 200}
    rating = action.rating if action.rating in allowed else 100
    result = process_task_payment(action.task_id, rating)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    # Broadcast updates
    await routing_logic.broadcast_to_session(result.get("user_id", action.task_id), json.dumps({
        "type": "task_update",
        "task_id": action.task_id,
        "status": "paid",
        "payout": result.get("actual_reward"),
        "net_reward": result.get("net_reward"),
        "rating": rating
    }))
    await routing_logic.broadcast_to_admins(json.dumps({"type": "admin_refresh_tasks"}))
    return result

# v1.5 AI Optimizer
@router.post("/optimizer/toggle")
async def toggle_optimizer(active: bool = Body(..., embed=True), admin=Depends(get_current_admin)):
    gamestate.optimizer_active = active
    return {"status": "ok", "optimizer_active": gamestate.optimizer_active}

@router.post("/optimizer/prompt")
async def set_optimizer_prompt(prompt: str = Body(..., embed=True), admin=Depends(get_current_admin)):
    gamestate.optimizer_prompt = prompt
    return {"status": "ok", "optimizer_prompt": gamestate.optimizer_prompt}

@router.get("/controls/state")
async def get_control_state(admin=Depends(get_current_admin)):
    """Get current state of all admin controls"""
    import time
    return {
        "optimizer_active": gamestate.optimizer_active,
        "agent_response_window": gamestate.agent_response_window,
        "hyper_visibility_mode": gamestate.hyper_visibility_mode.value,
        "chernobyl_mode": gamestate.chernobyl_mode.value,
        "temperature": gamestate.temperature,
        "power_capacity": gamestate.power_capacity,
        "power_load": gamestate.power_load,
        "power_boost_end_time": gamestate.power_boost_end_time,
        "server_time": time.time(),
        "shift_offset": gamestate.global_shift_offset,
        "is_overloaded": gamestate.is_overloaded
    }

# v1.4 Endpoints

class TimerAction(BaseModel):
    seconds: int

@router.post("/timer")
async def set_timer(action: TimerAction, admin=Depends(get_current_admin)):
    import json
    from ..logic.routing import routing_logic

    gamestate.agent_response_window = action.seconds

    await routing_logic.broadcast_global(json.dumps({
        "type": "gamestate_update",
        "agent_window": gamestate.agent_response_window
    }))

    return {"status": "ok", "window": gamestate.agent_response_window}

@router.post("/power/buy")
async def buy_power(admin=Depends(get_current_admin)):
    cost = 1000
    if gamestate.treasury_balance >= cost:
        gamestate.treasury_balance -= cost
        gamestate.power_capacity += 50
        
        # v1.7 Power Timer (30 mins)
        import time
        gamestate.power_boost_end_time = time.time() + (30 * 60)
        
        return {
            "status": "bought", 
            "capacity": gamestate.power_capacity, 
            "balance": gamestate.treasury_balance,
            "end_time": gamestate.power_boost_end_time
        }
    else:
        raise HTTPException(status_code=400, detail="Insufficient Treasury Funds")

class LabelUpdate(BaseModel):
    labels: Dict[str, str]

@router.post("/labels")
async def save_labels(action: LabelUpdate, admin=Depends(get_current_admin)):
    import json
    import os
    try:
        with open("data/admin_labels.json", "w") as f:
            json.dump(action.labels, f)
        return {"status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/labels")
async def get_labels(admin=Depends(get_current_admin)):
    import json
    import os
    if os.path.exists("data/admin_labels.json"):
        try:
            with open("data/admin_labels.json", "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

@router.post("/debug/treasury")
async def set_treasury(amount: int = Body(..., embed=True), admin=Depends(get_current_admin)):
    gamestate.treasury_balance = amount
    return {"status": "ok", "treasury": gamestate.treasury_balance}

# v1.6 Root Controls
class SystemConstants(BaseModel):
    tax_rate: float
    power_cap: float
    temp_threshold: float = 350.0
    temp_reset_val: float = 80.0
    temp_min: float = 20.0

    # Costs
    cost_base: float = 10.0
    cost_user: float = 5.0
    cost_autopilot: float = 10.0
    cost_low_latency: float = 30.0
    cost_optimizer: float = 15.0

    # Task Rewards
    task_reward_default: int = 100
    task_reward_low: int = 75
    task_reward_mid: int = 125
    task_reward_high: int = 175
    task_reward_party: int = 200

@router.post("/root/update_constants")
async def update_constants(data: SystemConstants, admin=Depends(get_current_admin)):
    """Update game constants logic (admin/root)"""
    gamestate.tax_rate = data.tax_rate
    gamestate.power_capacity = data.power_cap
    gamestate.TEMP_THRESHOLD = data.temp_threshold
    gamestate.TEMP_RESET_VALUE = data.temp_reset_val
    gamestate.TEMP_MIN = data.temp_min
    
    # Update Costs
    gamestate.COST_BASE = data.cost_base
    gamestate.COST_PER_USER = data.cost_user
    gamestate.COST_PER_AUTOPILOT = data.cost_autopilot
    gamestate.COST_LOW_LATENCY = data.cost_low_latency
    gamestate.COST_OPTIMIZER_ACTIVE = data.cost_optimizer

    # Task Rewards
    gamestate.task_reward_default = data.task_reward_default
    gamestate.task_reward_low = data.task_reward_low
    gamestate.task_reward_mid = data.task_reward_mid
    gamestate.task_reward_high = data.task_reward_high
    gamestate.task_reward_party = data.task_reward_party

    # Log Action
    from ..database import SessionLocal, SystemLog
    import json
    db = SessionLocal()
    db.add(SystemLog(event_type="ROOT", message=f"Constants Updated by {admin.username}", data=json.dumps(data.dict())))
    db.commit()
    db.close()
    
    # Broadcast update so Admin Dashboards reflect changes
    from ..logic.routing import routing_logic
    import json
    await routing_logic.broadcast_global(json.dumps({
        "type": "gamestate_update",
        "power_cap": gamestate.power_capacity,
        "temp_threshold": gamestate.TEMP_THRESHOLD
    }))
    
    return {"status": "updated", "values": data.dict()}

@router.get("/root/state")
async def get_root_state(admin=Depends(get_current_root)):
    """ROOT ONLY: Get full system state for initialization"""
    return {
        "tax_rate": gamestate.tax_rate,
        "power_cap": gamestate.power_capacity,
        "current_load": gamestate.power_load,
        "treasury": gamestate.treasury_balance,
        "optimizer_active": gamestate.optimizer_active,
        "temp_threshold": gamestate.TEMP_THRESHOLD,
        "temp_reset_val": gamestate.TEMP_RESET_VALUE,
        "temp_min": gamestate.TEMP_MIN,
        "costs": {
            "base": gamestate.COST_BASE,
            "user": gamestate.COST_PER_USER,
            "autopilot": gamestate.COST_PER_AUTOPILOT,
            "low_latency": gamestate.COST_LOW_LATENCY,
            "optimizer": gamestate.COST_OPTIMIZER_ACTIVE
        },
        "task_rewards": {
            "default": gamestate.task_reward_default,
            "low": gamestate.task_reward_low,
            "mid": gamestate.task_reward_mid,
            "high": gamestate.task_reward_high,
            "party": gamestate.task_reward_party
        }
    }

@router.get("/system_logs")
async def get_system_logs(admin=Depends(get_current_admin)):
    from ..database import SessionLocal, SystemLog
    db = SessionLocal()
    logs = db.query(SystemLog).order_by(SystemLog.timestamp.desc()).limit(100).all()
    db.close()
    return logs

@router.post("/system_logs/reset")
async def reset_system_logs(admin=Depends(get_current_admin)):
    from ..database import SessionLocal, SystemLog
    db = SessionLocal()
    db.query(SystemLog).delete()
    db.commit()
    db.close()
    return {"status": "ok"}

@router.post("/root/reset")
async def reset_system(admin=Depends(get_current_admin)):
    """Full System Wipe"""
    db = SessionLocal()
    try:
        # 1. Truncate Logs
        db.query(SystemLog).delete()
        db.query(ChatLog).delete()
        
        # 2. Reset Users
        users = db.query(User).filter(User.role == UserRole.USER).all()
        for u in users:
            u.credits = 100
            u.is_locked = False
            u.status_level = "low"
        
        # 3. Clear Tasks
        db.query(Task).delete()
        
        db.commit()
        
        # 4. Reset Gamestate
        gamestate.reset_state()
        
        # 5. Broadcast
        await routing_logic.broadcast_global('{"type": "system_reset"}')
        
        return {"status": "system_reset_complete"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# --- AI CONFIGURATION (ROOT) ---
class AIConfigUpdate(BaseModel):
    optimizer_prompt: str
    autopilot_model: str

@router.get("/root/ai_config")
async def get_ai_config(admin=Depends(get_current_root)):
    """ROOT ONLY: Get AI configuration"""
    return {
        "status": "ok",
        "optimizer_prompt": gamestate.optimizer_prompt,
        "autopilot_model": gamestate.llm_config_hyper.model_name,
        "optimizer_active": gamestate.optimizer_active,
        "test_mode": gamestate.test_mode
    }

@router.post("/root/ai_config")
async def update_ai_config(config: AIConfigUpdate, admin=Depends(get_current_root)):
    """ROOT ONLY: Update AI configuration"""
    # Update gamestate
    gamestate.optimizer_prompt = config.optimizer_prompt
    gamestate.llm_config_hyper.model_name = config.autopilot_model
    
    # Log action
    from ..database import SessionLocal, SystemLog
    import json
    db = SessionLocal()
    db.add(SystemLog(
        event_type="ROOT", 
        message=f"AI Config updated by {admin.username}",
        data=json.dumps(config.dict())
    ))
    db.commit()
    db.close()
    
    return {"status": "ok", "config": config.dict()}

@router.post("/root/restart")
async def restart_server(admin=Depends(get_current_root)):
    """ROOT ONLY: Restart the server process"""
    import subprocess
    import sys
    import os
    
    # Log action
    from ..database import SessionLocal, SystemLog
    db = SessionLocal()
    db.add(SystemLog(event_type="ROOT", message=f"Server RESTART initiated by {admin.username}"))
    db.commit()
    db.close()
    
    # Broadcast shutdown warning
    await routing_logic.broadcast_global('{"type": "server_restart", "message": "Server restarting in 3 seconds..."}')
    
    # Spawn a detached process to restart the server
    # This script will: wait 2s, kill current process, start new one
    restart_script = f"""
import time
import os
import signal
import subprocess
time.sleep(2)
os.kill({os.getpid()}, signal.SIGTERM)
time.sleep(1)
subprocess.Popen(['{sys.executable}', 'run.py'], cwd='{os.path.dirname(os.path.dirname(os.path.dirname(__file__)))}')
"""
    subprocess.Popen([sys.executable, '-c', restart_script], start_new_session=True)
    
    return {"status": "restarting", "message": "Server will restart in ~3 seconds"}

@router.post("/root/factory_reset")
async def factory_reset(admin=Depends(get_current_root)):
    """ROOT ONLY: Delete database and restart with fresh data"""
    import subprocess
    import sys
    import os
    
    # Log action (will be deleted but good for immediate debugging)
    from ..database import SessionLocal, SystemLog
    db = SessionLocal()
    db.add(SystemLog(event_type="ROOT", message=f"FACTORY RESET initiated by {admin.username}"))
    db.commit()
    db.close()
    
    # Broadcast shutdown warning
    await routing_logic.broadcast_global('{"type": "factory_reset", "message": "System will be wiped and restarted in 5 seconds..."}')
    
    # Find database path and labels file path
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    db_path = os.path.join(data_dir, 'iris.db')
    labels_path = os.path.join(data_dir, 'admin_labels.json')
    
    # Spawn a detached process to delete DB and restart
    reset_script = f"""
import time
import os
import signal
import subprocess
time.sleep(3)
# Delete database
if os.path.exists('{db_path}'):
    os.remove('{db_path}')
    print('Database deleted.')
# Delete custom labels file
if os.path.exists('{labels_path}'):
    os.remove('{labels_path}')
    print('Custom labels deleted.')
os.kill({os.getpid()}, signal.SIGTERM)
time.sleep(1)
subprocess.Popen(['{sys.executable}', 'run.py'], cwd='{os.path.dirname(os.path.dirname(os.path.dirname(__file__)))}')
"""
    subprocess.Popen([sys.executable, '-c', reset_script], start_new_session=True)
    
    return {"status": "resetting", "message": "Database will be deleted and server restarted in ~5 seconds"}
