from fastapi import WebSocket
from sqlalchemy.orm import Session
from ..database import User, UserRole
from .chat_service import ChatService
from .task_service import TaskService
from .admin_service import AdminService
import json

class Dispatcher:
    """
    Central router for WebSocket messages (Hotfix v1.1).
    - Inspects User Role (User/Agent/Admin).
    - Routes to appropriate Service (Chat, Task, Admin).
    """
    def __init__(self):
        self.chat_service = ChatService()
        self.task_service = TaskService()
        self.admin_service = AdminService()

    async def handle_message(self, message: dict, user: User, db: Session, websocket: WebSocket):
        msg_type = message.get("type", "")
        
        # 1. ADMIN Routing
        if user.role == UserRole.ADMIN or user.role == UserRole.ROOT:
            # Route all admin messages (including 'admin_' prefied or specific commands) to AdminService
            await self.admin_service.handle_admin_command(db, user, message, websocket)
            return

        # 2. TASK Routing (User only)
        if user.role == UserRole.USER and msg_type in ["task_request", "task_submit"]:
            if msg_type == "task_request":
                await self.task_service.handle_task_request(db, user, websocket)
            elif msg_type == "task_submit":
                await self.task_service.handle_task_submit(db, user, message, websocket)
            return

        # 3. CHAT Routing (Default for all remaining)
        if user.role == UserRole.AGENT:
            await self.chat_service.handle_agent_message(db, user, message, websocket)
        elif user.role == UserRole.USER:
            # Chat, Action, Typing Sync, Report, etc.
            if msg_type in ["typing_start", "typing_stop"]:
                 await self.chat_service.handle_typing_indicator(user, message, websocket)
            else:
                 await self.chat_service.handle_user_message(db, user, message, websocket)

dispatcher_service = Dispatcher()
