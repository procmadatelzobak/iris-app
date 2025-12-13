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
        # User ID is assumed to map directly to Session ID for simplest case (User 1 -> Session 1)
        # In a real app, mapped via DB. Here implicit as per spec 3.1
        # User ID X is permanently bound to Session X.
        user_id = session_id 
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                await connection.send_text(message)
        
        # 2. Send to AGENT currently routed to this session
        # SessionID = (AgentID + Shift) % Total
        # Therefore, we need to find which Agent ID maps to this Session ID
        # AgentID = (SessionID - Shift) % Total
        # Note: Handling python modulo with negative numbers correctly
        
        # However, it's easier to iterate all connected agents and calculate their current session
        shift = gamestate.global_shift_offset
        total = settings.TOTAL_SESSIONS
        
        for agent_id, connections in self.agent_connections.items():
            # Calculate what session this agent is currently seeing
            # Note: Agent IDs might need offset if they don't start at 0 or 1.
            # Let's assume Agent ID 1..8 and Session 1..8 for simplicity
            # But modulo math is 0-indexed.
            # Let's align on 0-indexed logic internally:
            # Agent Index (0-7) -> Session Index (0-7)
            # AgentId = AgentIndex + 1
            
            agent_index = agent_id - 1
            session_index = (agent_index + shift) % total
            current_session_id = session_index + 1
            
            if current_session_id == session_id:
                for connection in connections:
                    await connection.send_text(message)

    async def broadcast_to_admins(self, message: str):
        for connection in self.admin_connections:
            await connection.send_text(message)

routing_logic = ConnectionManager()
