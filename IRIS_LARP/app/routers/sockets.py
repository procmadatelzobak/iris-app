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

    await routing_logic.connect(websocket, user.role, user.id)
    try:
        while True:
            data = await websocket.receive_text()
            # Simple Echo / Command handler
            # In real app: parse JSON, save to DB, route to other party
            msg_data = {}
            try:
                msg_data = json.loads(data)
            except:
                msg_data = {"content": data}

            # ROUTING LOGIC
            # If User sends: Route to their Session (User + Agent)
            # If Agent sends: Route to their Current Session (Agent + Shift -> Session)
            
            if user.role == UserRole.USER:
                # User is bound to Session ID = User ID
                session_id = user.id
                await routing_logic.broadcast_to_session(session_id, json.dumps({
                    "sender": user.username,
                    "role": "user",
                    "content": msg_data.get("content")
                }))
                
            elif user.role == UserRole.AGENT:
                # Agent routed to Session based on Shift
                # AgentIndex (0-7) = User.id - 1
                # SessionIndex = (AgentIndex + Shift) % Total
                # SessionID = SessionIndex + 1
                shift = gamestate.global_shift_offset
                total = settings.TOTAL_SESSIONS
                agent_index = user.id - 1
                
                # Sanity check if ID > total
                session_index = (agent_index + shift) % total
                session_id = session_index + 1
                
                await routing_logic.broadcast_to_session(session_id, json.dumps({
                    "sender": user.username,
                    "role": "agent",
                    "content": msg_data.get("content"),
                    "session_id": session_id
                }))

            elif user.role == UserRole.ADMIN:
                # Admin commands
                if msg_data.get("type") == "shift_command":
                    new_shift = gamestate.increment_shift()
                    await routing_logic.broadcast_to_admins(json.dumps({"type": "gamestate_update", "shift": new_shift}))
                    # TODO: Notify all agents they have switched sessions?
                    
    except WebSocketDisconnect:
        routing_logic.disconnect(websocket, user.role, user.id)
