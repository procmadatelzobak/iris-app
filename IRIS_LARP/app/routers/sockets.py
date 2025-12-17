from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from typing import Annotated
from ..logic.routing import routing_logic
from ..logic.gamestate import gamestate
from ..dependencies import get_current_user
from ..database import User, UserRole, SessionLocal, ChatLog
from ..config import settings
from ..services.dispatcher import dispatcher_service
import json
import asyncio
import time
from jose import jwt, JWTError
from sqlalchemy.exc import SQLAlchemyError

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
        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()
        db.close()
        return user
    except JWTError:
        return None

# --- v1.4 Latency Monitor ---
async def monitor_latency():
    """Background task to check for agent response timeouts."""
    while True:
        try:
            await asyncio.sleep(5)
            now = time.time()
            limit = gamestate.agent_response_window
            
            # Iterate over pending responses to check for timeouts
            # Uses GAMESTATE now
            for session_id in list(gamestate.pending_responses.keys()):
                start_time = gamestate.pending_responses.get(session_id)
                if start_time and (now - start_time > limit):
                     # Timeout!
                     gamestate.mark_session_timeout(session_id)
                     await routing_logic.send_timeout_error_to_user(session_id)
                     await routing_logic.send_timeout_to_agent(session_id)
                
        except Exception as e:
            print(f"Latency Monitor Error: {e}")
            await asyncio.sleep(5)

@router.on_event("startup")
async def startup_event():
    asyncio.create_task(monitor_latency())

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
    logical_id = None
    if user.role == UserRole.AGENT or user.role == UserRole.USER:
        logical_id = get_logical_id(user.username, user.role.value)

    await routing_logic.connect(websocket, user.role, user.id, logical_id=logical_id)
    
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
    if user.role == UserRole.ADMIN:
        # Send GameState
        await websocket.send_text(json.dumps({
            "type": "init",
            "shift": gamestate.global_shift_offset,
            "temperature": gamestate.temperature,
            "online": routing_logic.get_online_status()
        }))
    

    
    # Send Custom Labels (v1.4)
    if user.role != UserRole.ADMIN:
        from ..config import BASE_DIR
        import os
        labels_path = BASE_DIR / "data" / "admin_labels.json"
        if os.path.exists(labels_path):
            with open(labels_path, "r") as f:
                try:
                    labels = json.load(f)
                    await websocket.send_text(json.dumps({
                        "type": "labels_update",
                        "labels": labels
                    }))
                except: pass

    
    # Send History on Connect (User/Agent logic)
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

            # Check for active or submitted task
            from ..database import Task, TaskStatus
            active_task = db.query(Task).filter(
                Task.user_id == user.id,
                Task.status.in_([TaskStatus.PENDING_APPROVAL, TaskStatus.ACTIVE, TaskStatus.SUBMITTED, TaskStatus.PAID, TaskStatus.COMPLETED])
            ).first()
            if active_task:
                await websocket.send_text(json.dumps({
                    "type": "task_update",
                    "is_active": True,
                    "task_id": active_task.id,
                    "status": active_task.status.value,
                    "description": active_task.prompt_desc,
                    "reward": active_task.reward_offered,
                    "submission": active_task.submission_content,
                    "rating": getattr(active_task, "final_rating", None)
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

            # Heartbeat - Ping/Pong
            if msg_data.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                continue

            # Persist and Route
            db_save = SessionLocal()
            try:
                await dispatcher_service.handle_message(msg_data, user, db_save, websocket)
            except Exception as e:
                print(f"WS Error: {e}")
                import traceback
                traceback.print_exc()
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
