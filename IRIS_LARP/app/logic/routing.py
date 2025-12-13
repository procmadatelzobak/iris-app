from typing import Dict, List, Optional
from fastapi import WebSocket
from ..config import settings
from ..database import UserRole
from .gamestate import gamestate

class ConnectionManager:
    def __init__(self):
        # Active connections: {user_id: [WebSocket]}
        self.user_connections: Dict[int, List[WebSocket]] = {}
        self.agent_connections: Dict[int, List[WebSocket]] = {}
        # Admin connections are just a list for broadcast
        self.admin_connections: List[WebSocket] = []
        
        # Autopilot State
        self.active_autopilots: Dict[int, bool] = {} # AgentID -> True/False
        self.hyper_histories: Dict[int, List[Dict[str, str]]] = {} # AgentID -> History

    async def connect(self, websocket: WebSocket, role: UserRole, user_id: int):
        await websocket.accept()
        if role == UserRole.USER:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)
        elif role == UserRole.AGENT:
            if user_id not in self.agent_connections:
                self.agent_connections[user_id] = []
            self.agent_connections[user_id].append(websocket)
        elif role == UserRole.ADMIN:
            self.admin_connections.append(websocket)

    def disconnect(self, websocket: WebSocket, role: UserRole, user_id: int):
        if role == UserRole.USER:
            if user_id in self.user_connections:
                if websocket in self.user_connections[user_id]:
                    self.user_connections[user_id].remove(websocket)
        elif role == UserRole.AGENT:
            if user_id in self.agent_connections:
                if websocket in self.agent_connections[user_id]:
                    self.agent_connections[user_id].remove(websocket)
        elif role == UserRole.ADMIN:
            if websocket in self.admin_connections:
                self.admin_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_session(self, session_id: int, message: str):
        # 1. Send to USER bound to this session
        user_id = session_id 
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                await connection.send_text(message)
        
        # 2. Send to AGENT currently routed to this session
        shift = gamestate.global_shift_offset
        total = settings.TOTAL_SESSIONS
        
        for agent_id, connections in self.agent_connections.items():
            agent_index = agent_id - 1
            session_index = (agent_index + shift) % total
            current_session_id = session_index + 1
            
            if current_session_id == session_id:
                for connection in connections:
                    await connection.send_text(message)

    async def broadcast_to_agent(self, agent_id: int, message: str):
        if agent_id in self.agent_connections:
            for connection in self.agent_connections[agent_id]:
                try: await connection.send_text(message)
                except: pass

    async def broadcast_to_admins(self, message: str):
        for connection in self.admin_connections:
            await connection.send_text(message)

    async def broadcast_global(self, message: str):
        # Admins
        for connection in self.admin_connections:
            try:
                await connection.send_text(message)
            except: pass
        
        # Agents
        for agent_id, connections in self.agent_connections.items():
            for connection in connections:
                try:
                     await connection.send_text(message)
                except: pass
        
        # Users
        for user_id, connections in self.user_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(message)
                except: pass

    def get_online_status(self):
        return {
            "users": list(self.user_connections.keys()),
            "agents": list(self.agent_connections.keys())
        }

routing_logic = ConnectionManager()
