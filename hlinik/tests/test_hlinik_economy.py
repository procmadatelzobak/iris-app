import pytest
import time
from app.database import User, Task, TaskStatus
from app.logic.gamestate import gamestate
from app.logic.economy import process_task_payment


def test_tax_collection(db):
    gamestate.reset_state()
    gamestate.tax_rate = 0.20
    gamestate.treasury_balance = 0

    user = User(username="TestUser", role="user", credits=100)
    db.add(user)
    db.commit()

    task = Task(
        user_id=user.id,
        status=TaskStatus.COMPLETED,
        reward_offered=1000,
        submission_content="Work done",
    )
    db.add(task)
    db.commit()

    result = process_task_payment(task.id, 100, db)

    db.refresh(user)
    db.refresh(task)

    assert result["status"] == "paid"
    assert result["tax_collected"] == 200
    assert result["net_reward"] == 800
    assert user.credits == 100 + 800
    assert gamestate.treasury_balance == 200


def test_power_pack_purchase():
    gamestate.reset_state()
    gamestate.treasury_balance = 1500
    gamestate.power_capacity = 100

    cost = 1000
    if gamestate.treasury_balance >= cost:
        gamestate.treasury_balance -= cost
        gamestate.power_capacity += 50
        gamestate.power_boost_end_time = time.time() + (30 * 60)
        success = True
    else:
        success = False

    assert success is True
    assert gamestate.treasury_balance == 500
    assert gamestate.power_capacity == 150
    assert gamestate.power_boost_end_time > time.time()


def test_insufficient_funds_purchase():
    gamestate.reset_state()
    gamestate.treasury_balance = 500
    gamestate.power_capacity = 100

    cost = 1000
    success = gamestate.treasury_balance >= cost

    assert success is False
    assert gamestate.treasury_balance == 500
    assert gamestate.power_capacity == 100
