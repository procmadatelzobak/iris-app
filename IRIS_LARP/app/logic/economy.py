from sqlalchemy.orm import Session
from ..database import SessionLocal, Task, TaskStatus, User
from .gamestate import gamestate

def process_task_payment(task_id: int, rating: int):
    """
    Processes the payment for a completed task.
    - Calculates reward based on rating (0-100%).
    - deducts Tax.
    - Updates User Credits.
    - Updates Treasury Balance.
    - Marks task as PAID.
    """
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return {"error": "Task not found"}
            
        if task.status == TaskStatus.PAID:
            return {"error": "Task already paid"}
            
        # Calculate Reward
        # Reward = Offered * (Rating / 100)
        base_reward = task.reward_offered
        actual_reward = int(base_reward * (rating / 100.0))
        
        # Calculate Tax
        tax_amount = int(actual_reward * gamestate.tax_rate)
        net_reward = actual_reward - tax_amount
        
        # Update User
        user = db.query(User).filter(User.id == task.user_id).first()
        if user:
            user.credits += net_reward
            
        # Update Treasury
        gamestate.treasury_balance += tax_amount
        
        # Update Task
        task.status = TaskStatus.PAID
        db.commit()
        
        return {
            "status": "paid",
            "base_reward": base_reward,
            "actual_reward": actual_reward,
            "tax_collected": tax_amount,
            "net_reward": net_reward,
            "treasury_balance": gamestate.treasury_balance
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()
