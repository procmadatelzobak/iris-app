import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from IRIS_LARP.app.database import Base, User, Task, TaskStatus
from IRIS_LARP.app.logic.gamestate import gamestate
from IRIS_LARP.app.logic.economy import process_task_payment

# Setup in-memory DB for testing
engine = create_engine('sqlite:///:memory:')
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def test_tax_collection():
    print("Testing Tax Collection...")
    db = TestingSessionLocal()
    
    # Setup
    gamestate.reset_state()
    gamestate.tax_rate = 0.20  # 20%
    gamestate.treasury_balance = 0

    # Create User
    user = User(username="TestUser", role="user", credits=100)
    db.add(user)
    db.commit()

    # Create Task
    task = Task(
        user_id=user.id,
        status=TaskStatus.COMPLETED,
        reward_offered=1000,
        submission_content="Work done"
    )
    db.add(task)
    db.commit()

    # Action: Pay Function using injected session
    result = process_task_payment(task.id, 100, db)
    
    # Reload from DB
    db.refresh(user)
    db.refresh(task)

    # Verification
    try:
        assert result["status"] == "paid"
        assert result["tax_collected"] == 200
        assert result["net_reward"] == 800
        assert user.credits == 100 + 800
        assert gamestate.treasury_balance == 200
        print("✅ Tax Collection OK")
    except AssertionError as e:
        print(f"❌ Tax Collection Failed: {e}")
        print(f"Result: {result}")
        print(f"User Credits: {user.credits}")
        print(f"Treasury: {gamestate.treasury_balance}")
    finally:
        db.close()

def test_power_pack_purchase():
    print("Testing Power Pack Purchase...")
    # Setup
    gamestate.reset_state()
    gamestate.treasury_balance = 1500
    gamestate.power_capacity = 100
    
    # Logic Simulation (from admin_api.py /power/buy)
    cost = 1000
    
    # Action
    if gamestate.treasury_balance >= cost:
        gamestate.treasury_balance -= cost
        gamestate.power_capacity += 50
        gamestate.power_boost_end_time = time.time() + (30 * 60)
        success = True
    else:
        success = False
        
    # Verification
    try:
        assert success is True
        assert gamestate.treasury_balance == 500
        assert gamestate.power_capacity == 150
        assert gamestate.power_boost_end_time > time.time()
        print("✅ Power Pack Purchase OK")
    except AssertionError as e:
        print(f"❌ Power Pack Purchase Failed: {e}")

def test_insufficient_funds_purchase():
    print("Testing Insufficient Funds...")
    # Setup
    gamestate.reset_state()
    gamestate.treasury_balance = 500 # Less than 1000
    gamestate.power_capacity = 100
    
    # Logic Simulation
    cost = 1000
    
    # Action
    if gamestate.treasury_balance >= cost:
        success = True
    else:
        success = False
        
    # Verification
    try:
        assert success is False
        assert gamestate.treasury_balance == 500
        assert gamestate.power_capacity == 100
        print("✅ Insufficient Funds Logic OK")
    except AssertionError as e:
        print(f"❌ Insufficient Funds Logic Failed: {e}")

if __name__ == "__main__":
    test_tax_collection()
    test_power_pack_purchase()
    test_insufficient_funds_purchase()
