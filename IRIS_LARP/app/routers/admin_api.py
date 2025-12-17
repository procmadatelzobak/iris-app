from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Optional
import json
import time

from pydantic import BaseModel

from ..dependencies import get_current_admin, get_current_root
from ..logic.llm_core import llm_service, LLMConfig, LLMProvider
from ..logic.gamestate import gamestate
from ..logic.routing import routing_logic
from ..services.admin_service import admin_service
from ..config import BASE_DIR
from ..database import SessionLocal, SystemConfig, User, Task, TaskStatus, ChatLog, UserRole, SystemLog, StatusLevel

# Persistent storage path for admin-defined session labels
LABELS_PATH = BASE_DIR / "data" / "admin_labels.json"

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
    prompt: Optional[str] = None

@router.post("/llm/config/{config_type}")
async def set_llm_config(config_type: str, payload: dict = Body(...), admin=Depends(get_current_admin)):
    try:
        await admin_service.update_llm_config(config_type, payload)
        return {"status": "ok", "config_type": config_type}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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

class PanicToggle(BaseModel):
    session_id: int
    target: str  # "user" or "agent"
    enabled: bool

@router.get("/panic/state/{session_id}")
async def get_panic_state(session_id: int, admin=Depends(get_current_admin)):
    return gamestate.get_panic_state(session_id)

@router.post("/panic/toggle")
async def set_panic(toggle: PanicToggle, admin=Depends(get_current_admin)):
    try:
        state = await admin_service.set_panic_mode_for_session(toggle.session_id, toggle.target, toggle.enabled)
        return {"status": "ok", "state": state}
    except ValueError as e:
         raise HTTPException(status_code=400, detail=str(e))

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
    try:
        await admin_service.fine_user(db, action.user_id, action.amount, action.reason)
    finally:
        db.close()
    return {"status": "ok"}

@router.post("/economy/bonus")
async def bonus_user(action: EconomyAction, admin=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        await admin_service.bonus_user(db, action.user_id, action.amount, action.reason)
    finally:
        db.close()
    return {"status": "ok"}

@router.post("/economy/toggle_lock")
async def toggle_lock(action: EconomyAction, admin=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        state = await admin_service.toggle_lock(db, action.user_id)
        if state == "USER_NOT_FOUND":
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "ok", "state": state}
    finally:
        db.close()

class StatusUpdate(BaseModel):
    user_id: int
    status: str

@router.post("/economy/set_status")
async def set_user_status(action: StatusUpdate, admin=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        await admin_service.set_user_status(db, action.user_id, action.status)
        return {"status": "ok", "new_level": action.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/economy/global_bonus")
async def global_bonus(action: EconomyAction, admin=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        count = await admin_service.global_bonus(db, action.amount, action.reason)
        return {"status": "ok", "count": count}
    finally:
        db.close()

@router.post("/economy/reset")
async def reset_economy(admin=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        count = await admin_service.reset_economy(db)
        return {"status": "reset", "count": count}
    finally:
        db.close()

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
    try:
        result = await admin_service.approve_task(db, action.task_id, action.reward, action.prompt_content)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    finally:
        db.close()

class GradeAction(BaseModel):
    task_id: int
    rating_modifier: float  # 0.0, 0.5, 1.0, 2.0

@router.post("/tasks/grade")
async def grade_task(action: GradeAction, admin=Depends(get_current_admin)):
    allowed_modifiers = {0.0, 0.5, 1.0, 2.0}
    modifier = action.rating_modifier if action.rating_modifier in allowed_modifiers else 1.0
    
    db = SessionLocal()
    try:
        result = await admin_service.grade_task(db, action.task_id, modifier)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/tasks/pay")
async def pay_task(action: TaskAction, admin=Depends(get_current_admin)):
    # Keep legacy direct call for now? Or implement in service.
    # Logic in service is 'grade_task' but that assumes modifier.
    # 'pay_task' uses rating. Let's redirect to economy helper directly or make a service method.
    # To keep this file clean, let's just use the direct helper import as it is strictly logic, not state.
    # But wait, we want to refrain from splitting logic.
    # 'pay_task' is legacy/manual override.
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

@router.get("/lore/data")
async def get_lore_data(admin=Depends(get_current_admin)):
    try:
        lore_data_dir = BASE_DIR.parent / "doc" / "iris" / "lore-web" / "data"
        roles_path = lore_data_dir / "roles.json"
        relations_path = lore_data_dir / "relations.json"
        
        data = {
            "roles": [],
            "relations": []
        }
        
        if roles_path.exists():
            with open(roles_path, "r") as f:
                data["roles"] = json.load(f)
                
        if relations_path.exists():
            with open(relations_path, "r") as f:
                data["relations"] = json.load(f)
                
        return data
    except Exception as e:
        print(f"Error loading lore data: {e}")
        return {"roles": [], "relations": [], "error": str(e)}

class TimerAction(BaseModel):
    seconds: int

@router.post("/timer")
async def set_timer(action: TimerAction, admin=Depends(get_current_admin)):
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
    LABELS_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(LABELS_PATH, "w") as f:
            json.dump(action.labels, f)
        return {"status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/labels")
async def get_labels(admin=Depends(get_current_admin)):
    if LABELS_PATH.exists():
        try:
            with open(LABELS_PATH, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

@router.post("/debug/treasury")
async def set_treasury(amount: int = Body(..., embed=True), admin=Depends(get_current_admin)):
    gamestate.treasury_balance = amount
    return {"status": "ok", "treasury": gamestate.treasury_balance}

class SystemConstants(BaseModel):
    tax_rate: float
    power_cap: float
    temp_threshold: float = 350.0
    temp_reset_val: float = 80.0
    temp_min: float = 20.0
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
    db = SessionLocal()
    try:
        await admin_service.update_constants(db, admin.username, data.dict())
        return {"status": "updated", "values": data.dict()}
    finally:
        db.close()

@router.get("/root/state")
async def get_root_state(admin=Depends(get_current_root)):
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
    db = SessionLocal()
    logs = db.query(SystemLog).order_by(SystemLog.timestamp.desc()).limit(100).all()
    db.close()
    return logs

@router.post("/system_logs/reset")
async def reset_system_logs(admin=Depends(get_current_admin)):
    db = SessionLocal()
    db.query(SystemLog).delete()
    db.commit()
    db.close()
    return {"status": "ok"}

@router.post("/root/reset")
async def reset_system(admin=Depends(get_current_admin)):
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

class AIConfigUpdate(BaseModel):
    optimizer_prompt: str
    autopilot_model: str

@router.get("/root/ai_config")
async def get_ai_config(admin=Depends(get_current_root)):
    return {
        "status": "ok",
        "optimizer_prompt": gamestate.optimizer_prompt,
        "autopilot_model": gamestate.llm_config_hyper.model_name,
        "optimizer_active": gamestate.optimizer_active,
        "test_mode": gamestate.test_mode
    }

@router.post("/root/ai_config")
async def update_ai_config(config: AIConfigUpdate, admin=Depends(get_current_root)):
    gamestate.optimizer_prompt = config.optimizer_prompt
    gamestate.llm_config_hyper.model_name = config.autopilot_model
    
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
    import subprocess
    import sys
    import os
    
    db = SessionLocal()
    db.add(SystemLog(event_type="ROOT", message=f"Server RESTART initiated by {admin.username}"))
    db.commit()
    db.close()
    
    await routing_logic.broadcast_global('{"type": "server_restart", "message": "Server restarting in 3 seconds..."}')
    
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
    import subprocess
    import sys
    import os
    
    db = SessionLocal()
    db.add(SystemLog(event_type="ROOT", message=f"FACTORY RESET initiated by {admin.username}"))
    db.commit()
    db.close()
    
    await routing_logic.broadcast_global('{"type": "factory_reset", "message": "System will be wiped and restarted in 5 seconds..."}')
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    db_path = os.path.join(data_dir, 'iris.db')
    labels_path = os.path.join(data_dir, 'admin_labels.json')
    
    reset_script = f"""
import time
import os
import signal
import subprocess
time.sleep(3)
if os.path.exists('{db_path}'):
    os.remove('{db_path}')
if os.path.exists('{labels_path}'):
    os.remove('{labels_path}')
os.kill({os.getpid()}, signal.SIGTERM)
time.sleep(1)
subprocess.Popen(['{sys.executable}', 'run.py'], cwd='{os.path.dirname(os.path.dirname(os.path.dirname(__file__)))}')
"""
    subprocess.Popen([sys.executable, '-c', reset_script], start_new_session=True)
    
    return {"status": "resetting", "message": "Database will be deleted and server restarted in ~5 seconds"}
