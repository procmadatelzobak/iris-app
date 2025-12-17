import json
from ..database import SessionLocal, Task, TaskStatus, SystemLog, User
from ..logic.routing import routing_logic
from ..logic.gamestate import gamestate
from fastapi import WebSocket

class TaskService:
    """
    Handles lifecycle of User Tasks.
    - Requests new tasks (generates via default reward).
    - Submits task solutions.
    - Notifies Admins of task updates.
    """
    async def handle_task_request(self, db: SessionLocal, user: User, websocket: WebSocket):
        # Log
        db_log = SessionLocal()
        db_log.add(SystemLog(event_type="ACTION", message=f"{user.username} requested task"))
        db_log.commit()
        db_log.close()
        
        existing = db.query(Task).filter(Task.user_id == user.id, Task.status.in_([
            TaskStatus.PENDING_APPROVAL,
            TaskStatus.ACTIVE,
            TaskStatus.SUBMITTED
        ])).first()
        
        if not existing:
            default_reward = gamestate.get_default_task_reward(user.status_level)
            new_task = Task(
                user_id=user.id,
                prompt_desc="Waiting for assignment...",
                reward_offered=default_reward,
                status=TaskStatus.PENDING_APPROVAL
            )
            db.add(new_task)
            db.commit()

            # Notify User
            await websocket.send_text(json.dumps({
                "type": "task_update",
                "is_active": True,
                "task_id": new_task.id,
                "status": "pending_approval",
                "reward": default_reward,
                "description": new_task.prompt_desc
            }))

            # Notify Admins
            await routing_logic.broadcast_to_admins(json.dumps({
                "type": "admin_refresh_tasks"
            }))
            
            # Log
            db_log = SessionLocal()
            db_log.add(SystemLog(event_type="TASK", message=f"{user.username} requested task"))
            db_log.commit()
            db_log.close()

    async def handle_task_submit(self, db: SessionLocal, user: User, msg_data: dict, websocket: WebSocket):
        submission_text = (msg_data.get("content") or "").strip()
        requested_id = msg_data.get("task_id")

        if not submission_text:
            await websocket.send_text(json.dumps({
                "type": "task_error",
                "message": "Odevzdání je prázdné."
            }))
            return

        query = db.query(Task).filter(Task.user_id == user.id, Task.status == TaskStatus.ACTIVE)
        if requested_id:
            query = query.filter(Task.id == requested_id)

        current_task = query.first()

        if not current_task:
            await websocket.send_text(json.dumps({
                "type": "task_error",
                "message": "Nemáš aktivní úkol k odevzdání."
            }))
            return

        current_task.submission_content = submission_text
        current_task.status = TaskStatus.SUBMITTED
        db.commit()

        await websocket.send_text(json.dumps({
            "type": "task_update",
            "task_id": current_task.id,
            "status": "submitted",
            "submission": submission_text,
            "description": current_task.prompt_desc,
            "reward": current_task.reward_offered
        }))

        await routing_logic.broadcast_to_admins(json.dumps({
            "type": "admin_refresh_tasks"
        }))

        db_log = SessionLocal()
        db_log.add(SystemLog(event_type="TASK", message=f"{user.username} submitted task #{current_task.id}"))
        db_log.commit()
        db_log.close()
