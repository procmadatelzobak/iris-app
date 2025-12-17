from typing import Dict, List, Optional
from fastapi import WebSocket
from ..config import settings
from ..database import UserRole
from .gamestate import gamestate
import json

class ConnectionManager:
    def __init__(self):
        # Active connections: {user_id: [WebSocket]}
        self.user_connections: Dict[int, List[WebSocket]] = {}
        self.agent_connections: Dict[int, List[WebSocket]] = {}
        # Mapping of DB IDs to logical routing IDs (agent1 -> 1, user1 -> 1)
        self.agent_logical_ids: Dict[int, int] = {}
        self.user_logical_ids: Dict[int, int] = {}
        # Admin connections are just a list for broadcast
        self.admin_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, role: UserRole, user_id: int, logical_id: Optional[int] = None):
        await websocket.accept()
        if role == UserRole.USER:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)
            if logical_id:
                self.user_logical_ids[user_id] = logical_id
        elif role == UserRole.AGENT:
            if user_id not in self.agent_connections:
                self.agent_connections[user_id] = []
            self.agent_connections[user_id].append(websocket)
            # Store logical routing id so session mapping is not tied to DB PK ordering
            if logical_id:
                self.agent_logical_ids[user_id] = logical_id
        elif role == UserRole.ADMIN:
            self.admin_connections.append(websocket)

    def disconnect(self, websocket: WebSocket, role: UserRole, user_id: int):
        if role == UserRole.USER:
            if user_id in self.user_connections:
                if websocket in self.user_connections[user_id]:
                    self.user_connections[user_id].remove(websocket)
                    if not self.user_connections[user_id]:
                        del self.user_connections[user_id]
                        if user_id in self.user_logical_ids:
                            del self.user_logical_ids[user_id]
        elif role == UserRole.AGENT:
            if user_id in self.agent_connections:
                if websocket in self.agent_connections[user_id]:
                    self.agent_connections[user_id].remove(websocket)
                    if not self.agent_connections[user_id]:
                        del self.agent_connections[user_id]
                        if user_id in self.agent_logical_ids:
                            del self.agent_logical_ids[user_id]
        elif role == UserRole.ADMIN:
            if websocket in self.admin_connections:
                self.admin_connections.remove(websocket)

    async def broadcast_global(self, message: str):
        # Users
        for cons in self.user_connections.values():
            for con in cons:
                try: await con.send_text(message)
                except: pass
        # Agents
        for cons in self.agent_connections.values():
            for con in cons:
                try: await con.send_text(message)
                except: pass
        # Admins
        for con in self.admin_connections:
            try: await con.send_text(message)
            except: pass

    async def broadcast_to_admins(self, message: str):
        for con in self.admin_connections:
            try: await con.send_text(message)
            except: pass

    async def broadcast_to_session(self, session_id: int, message: str, exclude_ws: Optional[WebSocket] = None):
        # 1. Users mapped to session_id
        for uid, lid in self.user_logical_ids.items():
            if lid == session_id:
                if uid in self.user_connections:
                    for con in self.user_connections[uid]:
                        if con != exclude_ws:
                            try: await con.send_text(message)
                            except: pass
        
        # 2. Agents mapped to session_id via Shift
        shift = gamestate.global_shift_offset
        total = getattr(settings, "TOTAL_SESSIONS", 8) 
        # AgentIndex = (SessionID - 1 - Shift) % Total
        # LogicalID = Index + 1
        agent_index = (session_id - 1 - shift) % total
        agent_lid = agent_index + 1
        
        # Find Agent UserID for this LogicalID
        for aid, lid in self.agent_logical_ids.items():
            if lid == agent_lid:
                if aid in self.agent_connections:
                    for con in self.agent_connections[aid]:
                        if con != exclude_ws:
                            try: await con.send_text(message)
                            except: pass

    async def broadcast_to_agent(self, agent_user_id: int, message: str, exclude_ws: Optional[WebSocket] = None):
        if agent_user_id in self.agent_connections:
            for con in self.agent_connections[agent_user_id]:
                if con != exclude_ws:
                    try: await con.send_text(message)
                    except: pass
    
    async def send_timeout_error_to_user(self, session_id: int):
        # Find user for session
        target_uid = None
        for uid, lid in self.user_logical_ids.items():
            if lid == session_id:
                target_uid = uid
                break
        
        if target_uid and target_uid in self.user_connections:
            msg = json.dumps({
                "type": "agent_timeout",
                "msg": "Agent neodpovídá. Prosím čekejte.",
                "session_id": session_id
            })
            for con in self.user_connections[target_uid]:
                try: await con.send_text(msg)
                except: pass

    async def send_timeout_to_agent(self, session_id: int):
        # Notify agent they are timed out
        shift = gamestate.global_shift_offset
        total = getattr(settings, "TOTAL_SESSIONS", 8)
        agent_index = (session_id - 1 - shift) % total
        agent_lid = agent_index + 1
        
        for aid, lid in self.agent_logical_ids.items():
            if lid == agent_lid:
                if aid in self.agent_connections:
                    msg = json.dumps({
                        "type": "error",
                        "msg": "Čas vypršel. Vaše odpověď byla zablokována.",
                        "session_id": session_id
                    })
                    for con in self.agent_connections[aid]:
                        try: await con.send_text(msg)
                        except: pass

    def get_online_status(self):
        return {
            "users": list(self.user_logical_ids.values()),
            "agents": list(self.agent_logical_ids.values())
        }

    def get_active_counts(self):
        return {
            "users": len(self.user_connections),
            "autopilots": sum(1 for v in gamestate.active_autopilots.values() if v)
        }

routing_logic = ConnectionManager()
