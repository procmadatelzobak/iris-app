import json
import os
import re
from ..database import SessionLocal, SystemLog, User
from ..logic.routing import routing_logic
from ..logic.gamestate import gamestate
from ..config import settings
from fastapi import WebSocket


def _session_id_from_username(username: str) -> int:
    """Extract logical session ID (1-8) from username like 'user3' -> 3."""
    match = re.search(r'\d+', username)
    return int(match.group()) if match else 0


class AdminService:
    async def handle_admin_command(self, db: SessionLocal, user: User, msg_data: dict, websocket: WebSocket):
        cmd_type = msg_data.get("type")
        
        if cmd_type == "action":
            action = msg_data.get("action")
            if action == "heat_tick":
                gamestate.manual_heat()
                await routing_logic.broadcast_global(json.dumps({
                    "type": "gamestate_update", 
                    "temperature": gamestate.temperature
                }))
                return

        if cmd_type == "shift_command":
            new_shift = gamestate.increment_shift()
            await routing_logic.broadcast_global(json.dumps({
                "type": "gamestate_update", 
                "shift": new_shift,
                "temperature": gamestate.temperature
            }))
        
        elif cmd_type == "set_shift_command":
            target = msg_data.get("value", 0)
            new_shift = gamestate.set_shift(int(target))
            await routing_logic.broadcast_global(json.dumps({
                "type": "gamestate_update", 
                "shift": new_shift,
                "temperature": gamestate.temperature
            }))
        
        elif cmd_type == "temperature_command": 
            level = msg_data.get("value", 0) 
            gamestate.set_temperature(float(level))
            
            await routing_logic.broadcast_global(json.dumps({
                "type": "gamestate_update", 
                "shift": gamestate.global_shift_offset,
                "temperature": gamestate.temperature
            }))

        elif cmd_type == "chernobyl_mode_command":
            from ..logic.gamestate import ChernobylMode
            mode_str = msg_data.get("mode", "normal")
            # Map string to enum
            if mode_str == "low_power":
                gamestate.chernobyl_mode = ChernobylMode.LOW_POWER
            elif mode_str == "overclock":
                gamestate.chernobyl_mode = ChernobylMode.OVERCLOCK
            else:
                gamestate.chernobyl_mode = ChernobylMode.NORMAL
            
            # Broadcast update
            await routing_logic.broadcast_global(json.dumps({
                "type": "gamestate_update", 
                "chernobyl_mode": gamestate.chernobyl_mode.value
            }))

        elif cmd_type == "reset_game":
            from ..logic.gamestate import ChernobylMode, HyperVisibilityMode
            
            # Soft Reset: Broadcast failover message, reset temp/labels, keep credits/power
            gamestate.set_temperature(gamestate.TEMP_RESET_VALUE)
            gamestate.chernobyl_mode = ChernobylMode.NORMAL
            gamestate.hyper_visibility_mode = HyperVisibilityMode.NORMAL
            
            # Reset custom labels (delete admin_labels.json)
            # Better way: config.BASE_DIR
            from ..config import BASE_DIR
            labels_path = BASE_DIR / "data" / "admin_labels.json"

            if os.path.exists(labels_path):
                os.remove(labels_path)
            
            # Reset GameState Dicts
            gamestate.panic_modes = {}
            gamestate.latest_user_messages = {}
            
            # Broadcast failover message to ALL users
            await routing_logic.broadcast_global(json.dumps({
                "type": "system_alert",
                "content": "⚠️ SYSTÉM REINICIALIZOVÁN ⚠️\nDošlo k přepnutí na záložní server v rámci failover protokolu.\nVšechny relace byly obnoveny. Pokračujte v práci.",
                "alert_type": "failover"
            }))
            
            # Also send gamestate update
            await routing_logic.broadcast_global(json.dumps({
                "type": "gamestate_update", 
                "shift": gamestate.global_shift_offset,
                "temperature": gamestate.temperature,
                "hyper_mode": "normal",
                "is_overloaded": False
            }))
            
        elif cmd_type == "admin_broadcast":
                content = msg_data.get("content", "SYSTEM ALERT")
                await routing_logic.broadcast_global(json.dumps({
                    "type": "message",
                    "sender": "ROOT",
                    "role": "admin",
                    "content": f"⚠ {content} ⚠",
                    "is_alert": True
                }))

        elif cmd_type == "admin_view_sync":
            view = msg_data.get("view", "monitor")
            await routing_logic.broadcast_to_admins(json.dumps({
                "type": "admin_view_sync",
                "view": view,
                "sender_id": user.id 
            }))
            
        elif cmd_type == "hyper_vis_command":
            mode_str = msg_data.get("mode", "normal")
            from ..logic.gamestate import HyperVisibilityMode
            mode_map = {
                "normal": HyperVisibilityMode.NORMAL,
                "blackbox": HyperVisibilityMode.BLACKBOX,
                "forensic": HyperVisibilityMode.FORENSIC,
                "ephemeral": HyperVisibilityMode.EPHEMERAL,
            }
            if mode_str in mode_map:
                gamestate.hyper_visibility_mode = mode_map[mode_str]
            
            # Log
            db_log = SessionLocal()
            db_log.add(SystemLog(event_type="ACTION", message=f"{user.username} changed HYPER to {mode_str}"))
            db_log.commit()
            db_log.close()
            
            await routing_logic.broadcast_global(json.dumps({
                "type": "gamestate_update",
                "hyper_mode": gamestate.hyper_visibility_mode.value
            }))

        elif cmd_type == "test_mode_toggle":
            enabled = msg_data.get("enabled", False)
            gamestate.test_mode = enabled
            # Broadcast status? Maybe just ack.
            await websocket.send_text(json.dumps({
                "type": "admin_ack",
                "msg": f"TEST MODE set to {enabled}"
            }))

        elif cmd_type == "panic_command":
            enabled = msg_data.get("enabled", False)
            # Global Panic set for all sessions
            for i in range(1, settings.TOTAL_SESSIONS + 1):
                    gamestate.set_panic_mode(i, "user", enabled)
                    gamestate.set_panic_mode(i, "agent", enabled)
            
            await routing_logic.broadcast_global(json.dumps({
                "type": "gamestate_update",
                "panic_global": enabled
            }))

    # --- REST API SUPPORT METHODS ---

    async def update_llm_config(self, config_type: str, payload: dict):
        from ..logic.llm_core import LLMConfig, LLMProvider
        
        if config_type == "task":
            gamestate.llm_config_task = LLMConfig(**payload)
        elif config_type == "hyper":
            gamestate.llm_config_hyper = LLMConfig(**payload)
        elif config_type == "optimizer":
            provider = payload.get("provider")
            model_name = payload.get("model_name")
            system_prompt = payload.get("system_prompt")
            prompt = payload.get("prompt")
            
            gamestate.llm_config_optimizer = LLMConfig(
                provider=provider,
                model_name=model_name,
                system_prompt=system_prompt
            )
            gamestate.optimizer_prompt = prompt
        elif config_type == "censor":
            gamestate.llm_config_censor = LLMConfig(**payload)
        else:
            raise ValueError("Invalid config type")
            
    async def set_panic_mode_for_session(self, session_id: int, target: str, enabled: bool):
        if target not in ["user", "agent"]:
             raise ValueError("Target must be 'user' or 'agent'")
        gamestate.set_panic_mode(session_id, target, enabled)
        return gamestate.get_panic_state(session_id)

    async def fine_user(self, db: SessionLocal, user_id: int, amount: int, reason: str):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            session_id = _session_id_from_username(user.username)
            user.credits -= amount
            if user.credits < 0 and not user.is_locked:
                user.is_locked = True
                await routing_logic.broadcast_to_session(session_id, json.dumps({"type": "lock_update", "locked": True}))
            db.commit()
            await routing_logic.broadcast_to_session(session_id, json.dumps({
                "type": "economy_update",
                "credits": user.credits,
                "msg": f"FINED: {reason}",
                "is_locked": user.is_locked
            }))

    async def bonus_user(self, db: SessionLocal, user_id: int, amount: int, reason: str):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            session_id = _session_id_from_username(user.username)
            user.credits += amount
            if user.credits < 0 and not user.is_locked:
                user.is_locked = True
                await routing_logic.broadcast_to_session(session_id, json.dumps({"type": "lock_update", "locked": True}))
            elif user.credits >= 0 and user.is_locked:
                user.is_locked = False
                await routing_logic.broadcast_to_session(session_id, json.dumps({"type": "lock_update", "locked": False}))

            db.commit()
            await routing_logic.broadcast_to_session(session_id, json.dumps({
                "type": "economy_update",
                "credits": user.credits,
                "msg": f"BONUS: {reason}",
                "is_locked": user.is_locked
            }))

    async def toggle_lock(self, db: SessionLocal, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            session_id = _session_id_from_username(user.username)
            user.is_locked = not user.is_locked
            db.commit()
            await routing_logic.broadcast_to_session(session_id, json.dumps({
                "type": "lock_update",
                "locked": user.is_locked
            }))
            return "LOCKED" if user.is_locked else "UNLOCKED"
        return "USER_NOT_FOUND"

    async def set_user_status(self, db: SessionLocal, user_id: int, status: str):
        if status not in ["low", "mid", "high", "party"]:
            raise ValueError("Invalid status")

        user = db.query(User).filter(User.id == user_id).first()
        if user:
            session_id = _session_id_from_username(user.username)
            user.status_level = status
            db.commit()
            await routing_logic.broadcast_to_session(session_id, json.dumps({
                "type": "theme_update",
                "theme": status
            }))
            return status

    async def global_bonus(self, db: SessionLocal, amount: int, reason: str):
        from ..database import UserRole
        users = db.query(User).filter(User.role == UserRole.USER).all()

        for user in users:
            session_id = _session_id_from_username(user.username)
            user.credits += amount
            await routing_logic.broadcast_to_session(session_id, json.dumps({
                "type": "economy_update",
                "credits": user.credits,
                "msg": f"GLOBAL STIMULUS: {reason}"
            }))
        db.commit()
        return len(users)

    async def reset_economy(self, db: SessionLocal):
        from ..database import UserRole
        users = db.query(User).filter(User.role == UserRole.USER).all()
        for user in users:
            session_id = _session_id_from_username(user.username)
            user.credits = 100
            user.is_locked = False
            await routing_logic.broadcast_to_session(session_id, json.dumps({
                "type": "user_status",
                "credits": 100,
                "is_locked": False
            }))
        db.commit()
        return len(users)

    async def approve_task(self, db: SessionLocal, task_id: int, reward: int = None, prompt_content: str = None):
        from ..database import Task, TaskStatus, StatusLevel
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError("Task not found")
            
        user = task.user
        
        # Reward Logic
        if reward is None or reward <= 0:
            level = user.status_level if user and user.status_level else StatusLevel.LOW
            reward = gamestate.get_default_task_reward(level)
            
        # Description Logic
        if not prompt_content or prompt_content.strip() == "" or prompt_content == "Waiting for assignment...":
            from ..logic.llm_core import llm_service
            user_profile = {
                "username": user.username if user else "unknown",
                "status_level": user.status_level.value if user and user.status_level else "low",
                "credits": user.credits if user else 0
            }
            try:
                prompt_content = await llm_service.generate_task_description(user_profile)
            except Exception:
                prompt_content = "Proveďte analýzu aktuálního stavu systému a navrhněte zlepšení."

        task.status = TaskStatus.ACTIVE
        task.reward_offered = reward
        task.prompt_desc = prompt_content
        db.commit()
        
        # Log
        db_log = SessionLocal()
        db_log.add(SystemLog(event_type="TASK", message=f"Task #{task.id} approved for {user.username}, reward: {reward}"))
        db_log.commit()
        db_log.close()
        
        # Notify
        user_session_id = _session_id_from_username(user.username) if user else 0
        await routing_logic.broadcast_to_session(
            user_session_id,
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
        return {"status": "approved", "task_id": task.id, "reward": reward}

    async def grade_task(self, db: SessionLocal, task_id: int, modifier: float):
        from ..logic.economy import process_task_payment
        result = process_task_payment(task_id, int(modifier * 100), db)
        
        if "error" in result:
             raise ValueError(result["error"])

        # Log
        from ..database import Task, ChatLog
        task = db.query(Task).filter(Task.id == task_id).first() 
        user = task.user if task else None
        
        db.add(SystemLog(
            event_type="ECONOMY",
            message=f"Task #{task_id} graded at {int(modifier*100)}%. Net: {result.get('net_reward')}"
        ))
        
        user_session_id = _session_id_from_username(user.username) if user else 0
        if user:
            task_name = task.prompt_desc[:50] if task and task.prompt_desc else "Úkol"
            db.add(ChatLog(
                session_id=user_session_id,
                sender_id=user.id,
                content=f"📋 Úkol '{task_name}...' vyhodnocen. Odměna: {result.get('net_reward', 0)} kreditů."
            ))
        db.commit()

        # Notify
        await routing_logic.broadcast_to_session(user_session_id, json.dumps({
            "type": "task_update",
            "task_id": task_id,
            "status": "paid",
            "payout": result.get("actual_reward"),
            "net_reward": result.get("net_reward"),
            "rating": int(modifier * 100)
        }))

        await routing_logic.broadcast_to_session(user_session_id, json.dumps({
            "type": "economy_update",
            "credits": result.get("net_reward", 0),
            "msg": f"Odměna za úkol: +{result.get('net_reward', 0)} CR"
        }))
        
        await routing_logic.broadcast_to_admins(json.dumps({"type": "admin_refresh_tasks"}))
        return result

    async def update_constants(self, db: SessionLocal, admin_username: str, data: dict):
        gamestate.update_reward_config(data) # Partial update
        # Manual update for rest
        if "power_cap" in data: gamestate.power_capacity = data["power_cap"]
        if "temp_threshold" in data: gamestate.TEMP_THRESHOLD = data["temp_threshold"]
        if "temp_reset_val" in data: gamestate.TEMP_RESET_VALUE = data["temp_reset_val"]
        if "temp_min" in data: gamestate.TEMP_MIN = data["temp_min"]
        
        if "cost_base" in data: gamestate.COST_BASE = data["cost_base"]
        if "cost_user" in data: gamestate.COST_PER_USER = data["cost_user"]
        if "cost_autopilot" in data: gamestate.COST_PER_AUTOPILOT = data["cost_autopilot"]
        if "cost_low_latency" in data: gamestate.COST_LOW_LATENCY = data["cost_low_latency"]
        if "cost_optimizer" in data: gamestate.COST_OPTIMIZER_ACTIVE = data["cost_optimizer"]
        
        db.add(SystemLog(event_type="ROOT", message=f"Constants Updated by {admin_username}", data=json.dumps(data)))
        db.commit()
        
        await routing_logic.broadcast_global(json.dumps({
            "type": "gamestate_update",
            "power_cap": gamestate.power_capacity,
            "temp_threshold": gamestate.TEMP_THRESHOLD
        }))
        return {"status": "updated"}

admin_service = AdminService()
