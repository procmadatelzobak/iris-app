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
        self.hyper_histories: Dict[int, List] = {}  # AgentID -> conversation history for autopilot
        # v1.4 Timer State
        self.session_last_msg_time: Dict[int, float] = {} # SessionID -> timestamp
        
        # Pending response tracking: session_id -> timestamp when user sent message
        # Used to track if agent needs to respond within timeout window
        self.pending_responses: Dict[int, float] = {}  # SessionID -> timestamp
        # Sessions that have timed out (agent can no longer respond)
        self.timed_out_sessions: Dict[int, float] = {}  # SessionID -> timeout timestamp

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
                    if not self.user_connections[user_id]:
                        del self.user_connections[user_id]
        elif role == UserRole.AGENT:
            if user_id in self.agent_connections:
                if websocket in self.agent_connections[user_id]:
                    self.agent_connections[user_id].remove(websocket)
                    if not self.agent_connections[user_id]:
                        del self.agent_connections[user_id]
        elif role == UserRole.ADMIN:
            if websocket in self.admin_connections:
                self.admin_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    def update_session_activity(self, session_id: int):
        import time
        self.session_last_msg_time[session_id] = time.time()

    def start_pending_response(self, session_id: int):
        """Mark that a user message was sent and we're waiting for agent response."""
        import time
        self.pending_responses[session_id] = time.time()
        # Clear any previous timeout for this session
        if session_id in self.timed_out_sessions:
            del self.timed_out_sessions[session_id]

    def clear_pending_response(self, session_id: int):
        """Agent responded in time, clear the pending state."""
        if session_id in self.pending_responses:
            del self.pending_responses[session_id]

    def mark_session_timeout(self, session_id: int):
        """Mark session as timed out - agent can no longer respond."""
        import time
        if session_id in self.pending_responses:
            del self.pending_responses[session_id]
        self.timed_out_sessions[session_id] = time.time()

    def is_session_timed_out(self, session_id: int) -> bool:
        """Check if session is currently in timed-out state."""
        return session_id in self.timed_out_sessions

    def clear_session_timeout(self, session_id: int):
        """Clear timeout state when user sends a new message."""
        if session_id in self.timed_out_sessions:
            del self.timed_out_sessions[session_id]

    async def send_timeout_error_to_user(self, session_id: int):
        """Send timeout error message to user for a specific session."""
        import json
        user_id = session_id  # Session ID matches User ID
        if user_id in self.user_connections:
            error_msg = json.dumps({
                "type": "agent_timeout",
                "content": "Agent nestihl odpovědět v časovém limitu. Požadavek se nepovedlo doručit.",
                "session_id": session_id
            })
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_text(error_msg)
                except:
                    pass

    async def send_timeout_to_agent(self, session_id: int):
        """Send timeout notification to agent for a specific session."""
        import json
        shift = gamestate.global_shift_offset
        total = settings.TOTAL_SESSIONS
        
        for agent_id, connections in self.agent_connections.items():
            agent_index = agent_id - 1
            session_index = (agent_index + shift) % total
            current_session_id = session_index + 1
            
            if current_session_id == session_id:
                timeout_msg = json.dumps({
                    "type": "session_timeout",
                    "session_id": session_id
                })
                for connection in connections:
                    try:
                        await connection.send_text(timeout_msg)
                    except:
                        pass

    async def broadcast_to_session(self, session_id: int, message: str):
        # 1. Send to USER bound to this session
        user_id = session_id 
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                try: await connection.send_text(message)
                except: pass
        
        # 2. Send to AGENT currently routed to this session
        shift = gamestate.global_shift_offset
        total = settings.TOTAL_SESSIONS
        
        for agent_id, connections in self.agent_connections.items():
            agent_index = agent_id - 1
            session_index = (agent_index + shift) % total
            current_session_id = session_index + 1
            
            if current_session_id == session_id:
                for connection in connections:
                    try: await connection.send_text(message)
                    except: pass

    async def broadcast_to_agent(self, agent_id: int, message: str):
        if agent_id in self.agent_connections:
            for connection in self.agent_connections[agent_id]:
                try: await connection.send_text(message)
                except: pass

    async def broadcast_to_admins(self, message: str):
        for connection in self.admin_connections:
            try: await connection.send_text(message)
            except: pass

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

    def get_active_counts(self):
        return {
            "users": len(self.user_connections),
            "autopilots": sum(1 for v in self.active_autopilots.values() if v)
        }

routing_logic = ConnectionManager()
