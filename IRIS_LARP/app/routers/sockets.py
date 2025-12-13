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
    if user.role == UserRole.ADMIN:
        # Send GameState
        await websocket.send_text(json.dumps({
            "type": "init",
            "shift": gamestate.global_shift_offset,
            "chernobyl": gamestate.chernobyl_value,
            "online": routing_logic.get_online_status()
        }))
    
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
            for log in history:
                sender_role = log.sender.role.value
                await websocket.send_text(json.dumps({
                    "sender": log.sender.username,
                    "role": sender_role,
                    "content": log.content,
                    "session_id": log.session_id if user.role == UserRole.AGENT else None
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
                        continue

                    if not content: continue
                    shift = gamestate.global_shift_offset
                    total = settings.TOTAL_SESSIONS
                    agent_index = agent_logical_id - 1
                    session_index = (agent_index + shift) % total
                    session_id = session_index + 1
                    
                    # Manual Override - If Agent types, they might want to clear history or just interject?
                    # Spec doesn't say. Let's assume manual typing doesn't break autopilot but maybe adds to context?
                    # For now, just save/send.
                    
                    # Save
                    log = ChatLog(session_id=session_id, sender_id=user.id, content=content)
                    db_save.add(log)
                    db_save.commit()
                    
                    await routing_logic.broadcast_to_session(session_id, json.dumps({
                        "sender": user.username,
                        "role": "agent",
                        "content": content,
                        "session_id": session_id
                    }))

                elif user.role == UserRole.USER:
                    if not content: continue
                    session_id = get_logical_id(user.username, "user")
                    # Save User Message
                    log = ChatLog(session_id=session_id, sender_id=user.id, content=content)
                    db_save.add(log)
                    db_save.commit()
                    
                    await routing_logic.broadcast_to_session(session_id, json.dumps({
                        "sender": user.username,
                        "role": "user",
                        "content": content
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
                                "session_id": session_id
                            }))

                elif user.role == UserRole.ADMIN:
                    # Admin commands
                    cmd_type = msg_data.get("type")
                    if cmd_type == "shift_command":
                        new_shift = gamestate.increment_shift()
                        # Broadcast Shift and Chernobyl to EVERYONE so UIs update
                        await routing_logic.broadcast_global(json.dumps({
                            "type": "gamestate_update", 
                            "shift": new_shift,
                            "chernobyl": gamestate.chernobyl_value
                        }))
                    
                    elif cmd_type == "chernobyl_command":
                        level = msg_data.get("level", 0)
                        gamestate.set_chernobyl(level)
                        await routing_logic.broadcast_global(json.dumps({
                            "type": "gamestate_update", 
                            "shift": gamestate.global_shift_offset,
                            "chernobyl": gamestate.chernobyl_value
                        }))

                    elif cmd_type == "reset_game":
                         # Placeholder
                         pass

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
