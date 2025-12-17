from typing import Dict, List, Optional
from fastapi import WebSocket
from ..config import settings
from ..database import UserRole
from .gamestate import gamestate
import json # Added for the new method

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
        
        # Autopilot State
        self.active_autopilots: Dict[int, bool] = {} # AgentID -> True/False
        self.hyper_histories: Dict[int, List] = {}  # AgentID -> conversation history for autopilot
        # v1.4 Timer State
        self.session_last_msg_time: Dict[int, float] = {} # SessionID -> timestamp
        
        # Pending response tracking: session_id -> timestamp when user sent message
        # Used to track if agent needs to respond within timeout window
        self.pending_responses: Dict[int, float] = {}  # SessionID -> timestamp
        # Sessions that have timed out (agent can no longer respond)
        self.timed_out_sessions: Dict[int, float] = {}  # SessionID -> timeout timestamp
        # Latest user message cache per session (for panic mode/context)
        self.latest_user_messages: Dict[int, str] = {}
        # Panic mode (full censorship) state per session
        self.panic_modes: Dict[int, Dict[str, bool]] = {}  # {session_id: {"user": False, "agent": False}}

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

    # ... (omitted) ...

    def get_online_status(self):
        return {
            "users": list(self.user_logical_ids.values()),
            "agents": list(self.agent_logical_ids.values())
        }

    def get_active_counts(self):
        return {
            "users": len(self.user_connections),
            "autopilots": sum(1 for v in self.active_autopilots.values() if v)
        }

routing_logic = ConnectionManager()
