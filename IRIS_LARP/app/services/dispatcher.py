from fastapi import WebSocket
from sqlalchemy.orm import Session
from ..database import User, UserRole
from .chat_service import ChatService
from .task_service import TaskService
from .admin_service import AdminService
import json

class Dispatcher:
    """
    Central router for WebSocket messages.
    - Inspects User Role (User/Agent/Admin).
    - Routes to appropriate Service (Chat, Task, Admin).
    """
    def __init__(self):
        self.chat_service = ChatService()
        self.task_service = TaskService()
        self.admin_service = AdminService()

    async def handle_message(self, message: dict, user: User, db: Session, websocket: WebSocket):
        msg_type = message.get("type", "")
        
        # --- AGENT ---
        if user.role == UserRole.AGENT:
            # All agent messages go to chat service
            await self.chat_service.handle_agent_message(db, user, message, websocket)
            
        # --- USER ---
        elif user.role == UserRole.USER:
            if msg_type in ["task_request"]:
                await self.task_service.handle_task_request(db, user, websocket)
            elif msg_type in ["task_submit"]:
                await self.task_service.handle_task_submit(db, user, message, websocket)
            else:
                # Chat, Action, Typing Sync, Report, etc.
                if msg_type in ["typing_start", "typing_stop"]:
                     await self.chat_service.handle_typing_indicator(user, message, websocket)
                else:
                     await self.chat_service.handle_user_message(db, user, message, websocket)

        # --- ADMIN ---
        elif user.role == UserRole.ADMIN:
            await self.admin_service.handle_admin_command(db, user, message, websocket)

dispatcher_service = Dispatcher()
