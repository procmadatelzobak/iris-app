from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from typing import Annotated
from ..logic.routing import routing_logic
from ..logic.gamestate import gamestate
from ..dependencies import get_current_user
from ..database import User, UserRole
from ..config import settings
import json
from jose import jwt, JWTError

router = APIRouter(tags=["sockets"])

# WebSocket cannot use standard Bearer header easily in browser JS without protocols
# We will accept token via Query Param for simplicity
async def get_user_from_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            return None
        # Minimal user object for routing
        # Ideally we fetch from DB, but for routing we just need ID and Role
        # Issue: we need the numerical ID. 
        # To avoid DB call on every connect/msg, let's embed ID in token or fetch once.
        # Fetching DB here is safer.
        from ..database import SessionLocal, User
        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()
        db.close()
        return user
    except JWTError:
        return None

@router.websocket("/ws/connect")
async def websocket_endpoint(websocket: WebSocket, token: str):
    user = await get_user_from_token(token)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Helper to get logical ID from username
    def get_logical_id(username: str, role: str) -> int:
        import re
        # Expect "userX" or "agentX"
        match = re.search(r'\d+', username)
        if match:
            return int(match.group())
        return 0 # Fallback

    # Connect
    await routing_logic.connect(websocket, user.role, user.id)
    
    # Notify Admins of new connection (if not admin)
    if user.role != UserRole.ADMIN:
        await routing_logic.broadcast_to_admins(json.dumps({
            "type": "status_update",
            "role": user.role.value,
            "id": user.id, # Uses raw DB ID, user1 might be ID 1 or 10 depending on seed order
            "username": user.username, # Send username for easier mapping
            "status": "online"
        }))

    # Admin Init
        # Admin Init
    if user.role == UserRole.ADMIN:
        # Send GameState
        await websocket.send_text(json.dumps({
            "type": "init",
            "shift": gamestate.global_shift_offset,
            "temperature": gamestate.temperature,
            "online": routing_logic.get_online_status()
        }))
    
    # ... (skipping unchanged lines)

    
    # Send History on Connect (User/Agent logic)
    from ..database import SessionLocal, ChatLog
    db = SessionLocal()
    try:
        # Determine which Session to load
        session_id_to_load = None
        if user.role == UserRole.USER:
            # User X is bound to Session X
            session_id_to_load = get_logical_id(user.username, "user")
        elif user.role == UserRole.AGENT:
            # Agent sees Session based on Shift
            shift = gamestate.global_shift_offset
            total = settings.TOTAL_SESSIONS
            # Agent 1 -> Index 0
            agent_logical_id = get_logical_id(user.username, "agent")
            agent_index = agent_logical_id - 1
            session_index = (agent_index + shift) % total
            session_id_to_load = session_index + 1
        
        if session_id_to_load:
            history = db.query(ChatLog).filter(ChatLog.session_id == session_id_to_load).order_by(ChatLog.timestamp).all()
            
            # Hyper Visibility Filter for Agents
            should_send_history = True
            if user.role == UserRole.AGENT:
                from ..logic.gamestate import HyperVisibilityMode
                if gamestate.hyper_visibility_mode == HyperVisibilityMode.BLACKBOX:
                    should_send_history = False
                elif gamestate.hyper_visibility_mode == HyperVisibilityMode.EPHEMERAL: # Not in Enum yet, but logic placeholder
                     # Assuming Ephemeral means empty history for now as per spec
                     should_send_history = False
            
            if should_send_history:
                for log in history:
                    sender_role = log.sender.role.value
                    await websocket.send_text(json.dumps({
                        "sender": log.sender.username,
                        "role": sender_role,
                        "content": log.content,
                        "session_id": log.session_id if user.role == UserRole.AGENT else None
                    }))
        
        # Send initial status for User
        if user.role == UserRole.USER:
             await websocket.send_text(json.dumps({
                "type": "user_status",
                "credits": user.credits,
                "is_locked": user.is_locked,
                "shift": gamestate.global_shift_offset
            }))

             # Check for active task
             from ..database import Task, TaskStatus
             active_task = db.query(Task).filter(Task.user_id == user.id, Task.status.in_([TaskStatus.PENDING_APPROVAL, TaskStatus.ACTIVE])).first()
             if active_task:
                 await websocket.send_text(json.dumps({
                     "type": "task_update",
                     "is_active": True,
                     "status": active_task.status.value,
                     "description": active_task.prompt_desc,
                     "reward": active_task.reward_offered
                 }))
        
        # Send initial status for Agent
        if user.role == UserRole.AGENT:
            await websocket.send_text(json.dumps({
                "type": "gamestate_update",
                "shift": gamestate.global_shift_offset,
                "temperature": gamestate.temperature,
                "session_id": session_id_to_load
            }))
    except Exception as e:
        print(f"Error loading history: {e}")
    finally:
        db.close()

    try:
        while True:
            data = await websocket.receive_text()
            msg_data = {}
            try:
                msg_data = json.loads(data)
            except:
                msg_data = {"content": data}

            content = msg_data.get("content")

            # Persist and Route
            db_save = SessionLocal()
            try:
                if user.role == UserRole.AGENT:
                    cmd_type = msg_data.get("type")
                    agent_logical_id = get_logical_id(user.username, "agent")

                    if cmd_type == "autopilot_toggle":
                        status = msg_data.get("status") # true/false
                        routing_logic.active_autopilots[agent_logical_id] = status
                        if not status:
                             # Clear history on OFF
                             routing_logic.hyper_histories[agent_logical_id] = []
                        # Sync Status? Ideally yes, but sound feedback is local.
                        # Let's verify toggle state sync later if needed.
                        continue

                    if cmd_type == "typing_sync":
                        content = msg_data.get("content", "")
                        await routing_logic.broadcast_to_agent(user.id, json.dumps({
                            "type": "typing_sync",
                            "sender": user.username, # To identify self vs mirror
                            "content": content
                        }))
                        continue

                    if not content: continue
                    shift = gamestate.global_shift_offset
                    total = settings.TOTAL_SESSIONS
                    agent_index = agent_logical_id - 1
                    session_index = (agent_index + shift) % total
                    session_id = session_index + 1

                    # v1.5 AI Optimizer && v2.0 Confirm Flow
                    final_content = content
                    was_rewritten = False

                    is_confirming = msg_data.get("confirm_opt", False) # Flag sent by client

                    if gamestate.optimizer_active and not is_confirming:
                        # Check Power
                        current_load = gamestate.power_load
                        cost = gamestate.COST_OPTIMIZER_ACTIVE
                        if current_load + cost <= gamestate.power_capacity:
                            # ACTIVE and POWER OK

                            # Broadcast Start
                            await routing_logic.broadcast_to_session(session_id, json.dumps({
                                "type": "optimizing_start"
                            }))

                            from ..logic.llm_core import llm_service
                            try:
                                rewritten = await llm_service.rewrite_message(content, gamestate.optimizer_prompt)
                                if rewritten and rewritten.strip():
                                    # v2.0: Send PREVIEW to Agent, do not broadcast/save yet
                                    await websocket.send_text(json.dumps({
                                        "type": "optimizer_preview",
                                        "original": content,
                                        "rewritten": rewritten
                                    }))
                                    continue # Stop processing, wait for confirmation
                            except Exception as e:
                                print(f"Optimizer Error: {e}")
                                # Fallback to sending original if error? Or fail?
                                # If error, let's just send original.

                    # Save (Rewritten or Original)
                    # If is_confirming, 'content' IS the rewritten version sent back by client
                    log = ChatLog(session_id=session_id, sender_id=user.id, content=final_content, is_optimized=is_confirming or was_rewritten)
                    db_save.add(log)
                    db_save.commit()

                    # Broadcast to Session (User sees final_content)
                    await routing_logic.broadcast_to_session(session_id, json.dumps({
                        "sender": user.username,
                        "role": "agent",
                        "content": final_content,
                        "session_id": session_id,
                        "id": log.id,
                        "is_optimized": log.is_optimized  # PHASE 27: Report immunity flag
                    }))
                    
                    # No feedback needed if confirmed, client knows.

                elif user.role == UserRole.USER:
                    cmd_type = msg_data.get("type")

                    # User Mirroring
                    if cmd_type == "typing_sync":
                        content = msg_data.get("content", "")
                        # Send to ALL sessions of this user (including other open tabs)
                        # broadcast_to_session sends to User+Agent. We specifically want "My other tabs".
                        # Use routing_logic.broadcast_to_user(user.id) if it existed, or broadcast_to_session and filter on client?
                        # Re-using broadcast_to_session targets Agent too (which is fine, Agent could see typing).
                        # But specific requirement: "broadcast to all connection of same user".
                        # Let's add that logic inline or helper.
                        if user.id in routing_logic.user_connections:
                            for conn in routing_logic.user_connections[user.id]:
                                if conn != websocket: # Don't echo back
                                    await conn.send_text(json.dumps({
                                        "type": "typing_sync",
                                        "sender": user.username,
                                        "content": content
                                    }))
                        continue

                    # Task Request
                    if cmd_type == "task_request":
                        from ..database import Task, TaskStatus
                        # Log
                        from ..database import SessionLocal, SystemLog 
                        db_log = SessionLocal()
                        db_log.add(SystemLog(event_type="ACTION", message=f"{user.username} requested task"))
                        db_log.commit()
                        db_log.close()
                        existing = db_save.query(Task).filter(Task.user_id == user.id, Task.status.in_([TaskStatus.PENDING_APPROVAL, TaskStatus.ACTIVE])).first()
                        if not existing:
                            new_task = Task(
                                user_id=user.id,
                                prompt_desc="Waiting for assignment...",
                                reward_offered=0,
                                status=TaskStatus.PENDING_APPROVAL
                            )
                            db_save.add(new_task)
                            db_save.commit()

                            # Notify User
                            await websocket.send_text(json.dumps({
                                "type": "task_update",
                                "is_active": True,
                                "status": "pending_approval"
                            }))

                            # Notify Admins
                            await routing_logic.broadcast_to_admins(json.dumps({
                                "type": "admin_refresh_tasks"
                            }))
                            
                            # Log
                            db_log = SessionLocal()
                            db_log.add(SystemLog(event_type="TASK", message=f"{user.username} requested task"))
                            db_log.commit()
                            db_log.close()
                        continue

                    # v1.7 Report Logic
                    if cmd_type == "report_message":
                        msg_id = msg_data.get("id")
                        # Verify DB
                        target_log = db_save.query(ChatLog).filter(ChatLog.id == msg_id).first()
                        if target_log:
                            if target_log.is_optimized:
                                # IMMUNITY
                                await websocket.send_text(json.dumps({
                                    "type": "report_denied",
                                    "reason": "SYSTEM_VERIFIED"
                                }))
                            else:
                                # Normal Report -> Heat Up
                                gamestate.report_anomaly()
                                target_log.was_reported = True
                                db_save.commit()
                                
                                # Broadcast new temp
                                await routing_logic.broadcast_global(json.dumps({
                                    "type": "gamestate_update", 
                                    "temperature": gamestate.temperature
                                }))
                                
                                # Ack
                                await websocket.send_text(json.dumps({
                                    "type": "report_accepted",
                                    "msg": "Report filed. Anomaly detected."
                                }))
                                
                                # Log
                                db_log = SessionLocal()
                                db_log.add(SystemLog(event_type="REPORT", message=f"{user.username} reported message {msg_id}"))
                                db_log.commit()
                                db_log.close()
                        continue

                    if not content: continue
                    
                    # Purgatory Mode Check: Fetch fresh status
                    db_user_check = db_save.query(User).filter(User.id == user.id).first()
                    is_purgatory = db_user_check.is_locked if db_user_check else False
                    
                    if is_purgatory:
                        # Block Chat - Allow only tasks (handled above)
                        # Optionally send error back
                        await websocket.send_text(json.dumps({
                           "type": "error",
                           "msg": "COMMUNICATION OFFLINE due to Debt."
                        }))
                        continue

                    session_id = get_logical_id(user.username, "user")
                    # Save User Message
                    log = ChatLog(session_id=session_id, sender_id=user.id, content=content)
                    db_save.add(log)
                    db_save.commit()
                    
                    await routing_logic.broadcast_to_session(session_id, json.dumps({
                        "sender": user.username,
                        "role": "user",
                        "content": content,
                        "id": log.id
                    }))
                    
                    # CHECK FOR AUTOPILOT
                    # Reverse Routing: Which Agent is on this Session?
                    # SessionID = (AgentIndex + Shift) % Total + 1
                    # AgentIndex = (SessionID - 1 - Shift) % Total
                    shift = gamestate.global_shift_offset
                    total = settings.TOTAL_SESSIONS
                    agent_index = (session_id - 1 - shift) % total
                    agent_logical_id = agent_index + 1 # This is the Agent mapped to this user
                    
                    if routing_logic.active_autopilots.get(agent_logical_id):
                        # 1. Update History
                        if agent_logical_id not in routing_logic.hyper_histories:
                            routing_logic.hyper_histories[agent_logical_id] = []
                        
                        history = routing_logic.hyper_histories[agent_logical_id]
                        history.append({"role": "user", "content": content})
                        
                        # 2. Generate Reply
                        from ..logic.llm_core import llm_service
                        reply = llm_service.generate_response(gamestate.llm_config_hyper, history)
                        
                        # 3. Add Reply to History
                        history.append({"role": "assistant", "content": reply})
                        
                        # 4. Save & Broadcast (As Agent)
                        # We need the Agent's User DB Object ID to save correctly?
                        # Or we can just use the UserID we calculated if we trust the mapping.
                        # Wait, ChatLog sender_id is a Foreign Key to Users table.
                        # We know Agent's logical ID. We need their DB ID. 
                        # This works if DB ID == Logical ID (due to seed).
                        # Let's assumes seeded IDs match: Agent 1 (user agent1) -> ID ~6.
                        # This is risky if IDs drift.
                        # Better: Query DB for user with username "agent{ID}".
                        agent_username = f"agent{agent_logical_id}"
                        agent_db_user = db_save.query(User).filter(User.username == agent_username).first()
                        
                        if agent_db_user and reply:
                            log_ai = ChatLog(session_id=session_id, sender_id=agent_db_user.id, content=reply)
                            db_save.add(log_ai)
                            db_save.commit()
                            
                            await routing_logic.broadcast_to_session(session_id, json.dumps({
                                "sender": agent_username,
                                "role": "agent",
                                "content": reply,
                                "session_id": session_id,
                                "id": log_ai.id
                            }))

                elif user.role == UserRole.ADMIN:
                    # Admin commands
                    cmd_type = msg_data.get("type")
                    if cmd_type == "shift_command":
                        new_shift = gamestate.increment_shift()
                        # Broadcast Shift and Temp to EVERYONE so UIs update
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
                    
                    elif cmd_type == "temperature_command": # Renamed from chernobyl_command
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
                            
                        # Broadcast? Usually mode change doesn't need broadcast, just the effect (value change)

                    elif cmd_type == "reset_game":
                        # Soft Reset: Broadcast failover message, reset temp/labels, keep credits/power
                        
                        # Reset temperature and modes
                        gamestate.set_temperature(gamestate.TEMP_RESET_VALUE)
                        gamestate.chernobyl_mode = ChernobylMode.NORMAL
                        gamestate.hyper_visibility_mode = HyperVisibilityMode.NORMAL
                        
                        # Reset custom labels (delete admin_labels.json)
                        import os
                        labels_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'admin_labels.json')
                        if os.path.exists(labels_path):
                            os.remove(labels_path)
                        
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
                        old_mode = gamestate.hyper_visibility_mode
                        from ..logic.gamestate import HyperVisibilityMode
                        if mode_str == "normal":
                            gamestate.hyper_visibility_mode = HyperVisibilityMode.NORMAL
                        elif mode_str == "blackbox":
                            gamestate.hyper_visibility_mode = HyperVisibilityMode.BLACKBOX
                        elif mode_str == "forensic":
                            gamestate.hyper_visibility_mode = HyperVisibilityMode.FORENSIC
                        
                        # Log
                        from ..database import SessionLocal, SystemLog
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

            finally:
                db_save.close()
                    
    except WebSocketDisconnect:
        routing_logic.disconnect(websocket, user.role, user.id)
        if user.role != UserRole.ADMIN:
            await routing_logic.broadcast_to_admins(json.dumps({
                "type": "status_update",
                "role": user.role.value,
                "id": user.id,
                "username": user.username,
                "status": "offline"
            }))
