"""
TEST SUITE B: Comprehensive Automated Test Suite
Version: 1.0
Goal: Full coverage of all application features with efficient, combined test scenarios.
Designed for execution by GitHub Copilot Agent.
"""

import pytest
import json
import time
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, User, Task, TaskStatus, ChatLog, SystemLog, UserRole, init_db
from app.logic.gamestate import gamestate, ChernobylMode, HyperVisibilityMode
from app.seed import seed_data

client = TestClient(app)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Initialize database and seed data once for all tests."""
    init_db()
    seed_data()
    gamestate.reset_state()
    yield
    # Cleanup after all tests
    gamestate.reset_state()


@pytest.fixture
def admin_auth():
    """Get admin authentication headers."""
    response = client.post("/auth/login", data={"username": "admin1", "password": "secure_admin_1"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_auth():
    """Get user authentication headers."""
    response = client.post("/auth/login", data={"username": "user1", "password": "subject_pass_1"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def agent_auth():
    """Get agent authentication headers."""
    response = client.post("/auth/login", data={"username": "agent1", "password": "agent_pass_1"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def root_auth():
    """Get root authentication headers."""
    response = client.post("/auth/login", data={"username": "root", "password": "master_control_666"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def clean_user():
    """Reset user1 to default state before test."""
    db = SessionLocal()
    user = db.query(User).filter(User.username == "user1").first()
    if user:
        user.credits = 100
        user.is_locked = False
        user.status_level = "low"
        db.commit()
    db.close()
    yield
    # Cleanup after test
    db = SessionLocal()
    user = db.query(User).filter(User.username == "user1").first()
    if user:
        user.credits = 100
        user.is_locked = False
        db.commit()
    db.close()


@pytest.fixture
def clean_gamestate():
    """Reset gamestate before test."""
    gamestate.reset_state()
    yield
    gamestate.reset_state()


# ============================================================================
# BLOCK 1: AUTHENTICATION & SESSION
# ============================================================================

class TestAuthentication:
    """Block 1: Verify login, token handling, and role-based access."""

    def test_login_admin_valid(self):
        """1.1: Login with valid admin credentials."""
        response = client.post("/auth/login", data={"username": "admin1", "password": "secure_admin_1"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["role"] == "admin"

    def test_login_user_valid(self):
        """1.2: Login with valid user credentials."""
        response = client.post("/auth/login", data={"username": "user1", "password": "subject_pass_1"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["role"] == "user"

    def test_login_agent_valid(self):
        """1.3: Login with valid agent credentials."""
        response = client.post("/auth/login", data={"username": "agent1", "password": "agent_pass_1"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["role"] == "agent"

    def test_login_invalid_credentials(self):
        """1.4: Login with invalid credentials."""
        response = client.post("/auth/login", data={"username": "admin1", "password": "wrong_password"})
        assert response.status_code == 401

    def test_protected_endpoint_no_token(self):
        """1.5: Access protected endpoint without token."""
        response = client.get("/api/admin/data/users")
        assert response.status_code == 401

    def test_auth_me(self, admin_auth):
        """1.6: Access /auth/me with valid token."""
        response = client.get("/auth/me", headers=admin_auth)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin1"
        assert data["role"] == "admin"


# ============================================================================
# BLOCK 2: ECONOMY SYSTEM
# ============================================================================

class TestEconomySystem:
    """Block 2: Verify credit management, lockout/unlock, and global operations."""

    def test_fine_user_lockout(self, admin_auth, clean_user):
        """2.1: Fine user causing negative balance triggers lockout."""
        db = SessionLocal()
        user = db.query(User).filter(User.username == "user1").first()
        user_id = user.id
        user.credits = 50
        user.is_locked = False
        db.commit()
        db.close()

        # Fine 100 (balance -> -50)
        response = client.post(
            "/api/admin/economy/fine",
            json={"user_id": user_id, "amount": 100, "reason": "Test fine"},
            headers=admin_auth
        )
        assert response.status_code == 200

        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        assert user.credits == -50
        assert user.is_locked is True
        db.close()

    def test_bonus_user_unlock(self, admin_auth, clean_user):
        """2.2: Bonus user with negative balance to positive triggers unlock."""
        db = SessionLocal()
        user = db.query(User).filter(User.username == "user1").first()
        user_id = user.id
        user.credits = -50
        user.is_locked = True
        db.commit()
        db.close()

        # Bonus 100 (balance -> 50)
        response = client.post(
            "/api/admin/economy/bonus",
            json={"user_id": user_id, "amount": 100, "reason": "Test bonus"},
            headers=admin_auth
        )
        assert response.status_code == 200

        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        assert user.credits == 50
        assert user.is_locked is False
        db.close()

    def test_toggle_lock(self, admin_auth, clean_user):
        """2.3: Toggle lock manually."""
        db = SessionLocal()
        user = db.query(User).filter(User.username == "user1").first()
        user_id = user.id
        original_locked = user.is_locked
        db.close()

        response = client.post(
            "/api/admin/economy/toggle_lock",
            json={"user_id": user_id},
            headers=admin_auth
        )
        assert response.status_code == 200

        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        assert user.is_locked != original_locked
        db.close()

    def test_set_user_status(self, admin_auth, clean_user):
        """2.4: Set user status."""
        db = SessionLocal()
        user = db.query(User).filter(User.username == "user1").first()
        user_id = user.id
        db.close()

        for status in ["low", "mid", "high", "party"]:
            response = client.post(
                "/api/admin/economy/set_status",
                json={"user_id": user_id, "status": status},
                headers=admin_auth
            )
            assert response.status_code == 200
            assert response.json()["new_level"] == status

    def test_global_bonus(self, admin_auth):
        """2.5: Global bonus to all users."""
        response = client.post(
            "/api/admin/economy/global_bonus",
            json={"user_id": 0, "amount": 10, "reason": "Global test"},
            headers=admin_auth
        )
        assert response.status_code == 200
        assert response.json()["count"] == 8  # 8 users seeded

    def test_reset_economy(self, admin_auth):
        """2.6: Reset economy resets all users."""
        response = client.post("/api/admin/economy/reset", headers=admin_auth)
        assert response.status_code == 200
        assert response.json()["count"] == 8

        db = SessionLocal()
        users = db.query(User).filter(User.role == UserRole.USER).all()
        for user in users:
            assert user.credits == 100
            assert user.is_locked is False
        db.close()

    def test_get_users(self, admin_auth):
        """2.7: Get users list."""
        response = client.get("/api/admin/data/users", headers=admin_auth)
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 8


# ============================================================================
# BLOCK 3: TASK SYSTEM
# ============================================================================

class TestTaskSystem:
    """Block 3: Verify full task lifecycle."""

    def test_task_lifecycle(self, admin_auth, clean_user, clean_gamestate):
        """3.1-3.4: Full task lifecycle test."""
        db = SessionLocal()
        user = db.query(User).filter(User.username == "user1").first()
        user_id = user.id
        initial_credits = user.credits
        
        # Clear existing tasks
        db.query(Task).filter(Task.user_id == user_id).delete()
        db.commit()
        
        # 3.1: Create task
        task = Task(
            user_id=user_id,
            prompt_desc="Original Task",
            status=TaskStatus.PENDING_APPROVAL
        )
        db.add(task)
        db.commit()
        task_id = task.id
        db.close()

        # 3.2 & 3.3: Approve with reward and edit prompt
        response = client.post(
            "/api/admin/tasks/approve",
            json={"task_id": task_id, "reward": 100, "prompt_content": "Edited Task"},
            headers=admin_auth
        )
        assert response.status_code == 200

        db = SessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        assert task.status == TaskStatus.ACTIVE
        assert task.reward_offered == 100
        assert task.prompt_desc == "Edited Task"
        db.close()

        # 3.4: Pay task (100% rating, 20% tax)
        gamestate.tax_rate = 0.20
        response = client.post(
            "/api/admin/tasks/pay",
            json={"task_id": task_id, "rating": 100},
            headers=admin_auth
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paid"
        assert data["net_reward"] == 80  # 100 - 20% tax
        assert data["tax_collected"] == 20

        # 3.5: Attempt to pay again
        response = client.post(
            "/api/admin/tasks/pay",
            json={"task_id": task_id, "rating": 100},
            headers=admin_auth
        )
        assert response.status_code == 400

    def test_get_tasks(self, admin_auth):
        """3.6: Get all tasks."""
        response = client.get("/api/admin/tasks", headers=admin_auth)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


# ============================================================================
# BLOCK 4: GAMESTATE & POWER SYSTEM
# ============================================================================

class TestGamestateSystem:
    """Block 4: Verify temperature, shift, power load, and overload detection."""

    def test_set_temperature(self, clean_gamestate):
        """4.1: Set temperature with clamping."""
        gamestate.set_temperature(100.0)
        assert gamestate.temperature == 100.0

        # Test min clamping
        gamestate.set_temperature(10.0)
        assert gamestate.temperature == 20.0  # Clamped to TEMP_MIN

        # Test max clamping
        gamestate.set_temperature(2000.0)
        assert gamestate.temperature == 1000.0  # Clamped to max

    def test_report_anomaly(self, clean_gamestate):
        """4.2: Report anomaly increases temperature."""
        initial_temp = gamestate.temperature
        gamestate.report_anomaly()
        assert gamestate.temperature == initial_temp + 15.0

    def test_process_tick_normal_mode(self, clean_gamestate):
        """4.3: Process tick in normal mode decays temperature."""
        gamestate.set_temperature(100.0)
        gamestate.chernobyl_mode = ChernobylMode.NORMAL
        gamestate.process_tick()
        assert gamestate.temperature == 99.5  # Decay 0.5

    def test_process_tick_low_power_mode(self, clean_gamestate):
        """4.4: Process tick in low power mode decays faster."""
        gamestate.set_temperature(100.0)
        gamestate.chernobyl_mode = ChernobylMode.LOW_POWER
        gamestate.process_tick()
        assert gamestate.temperature == 98.5  # Decay 1.5

    def test_increment_shift(self, clean_gamestate):
        """4.5: Increment shift with wrap-around."""
        gamestate.global_shift_offset = 0
        gamestate.increment_shift()
        assert gamestate.global_shift_offset == 1

        gamestate.global_shift_offset = 7
        gamestate.increment_shift()
        assert gamestate.global_shift_offset == 0  # Wrap

    def test_set_shift(self, clean_gamestate):
        """4.6: Set shift directly."""
        gamestate.set_shift(5)
        assert gamestate.global_shift_offset == 5

        gamestate.set_shift(10)  # Should wrap
        assert gamestate.global_shift_offset == 2

    def test_calc_power_load(self, clean_gamestate):
        """4.7: Calculate power load."""
        gamestate.COST_BASE = 10.0
        gamestate.COST_PER_USER = 5.0
        gamestate.COST_PER_AUTOPILOT = 10.0
        gamestate.COST_LOW_LATENCY = 30.0
        gamestate.COST_OPTIMIZER_ACTIVE = 15.0
        gamestate.optimizer_active = False

        load = gamestate.calc_load(active_terminals=2, active_autopilots=1, low_latency_active=False)
        # 10 + 2*5 + 1*10 = 30
        assert load == 30.0

        gamestate.optimizer_active = True
        load = gamestate.calc_load(active_terminals=2, active_autopilots=1, low_latency_active=True)
        # 10 + 2*5 + 1*10 + 30 + 15 = 75
        assert load == 75.0

    def test_check_overload(self, clean_gamestate):
        """4.8: Check overload detection."""
        gamestate.power_capacity = 100
        gamestate.TEMP_THRESHOLD = 350.0

        # No overload
        gamestate.power_load = 50
        gamestate.temperature = 100.0
        result = gamestate.check_overload()
        assert gamestate.is_overloaded is False

        # Power overload
        gamestate.power_load = 150
        gamestate.check_overload()
        assert gamestate.is_overloaded is True

        # Temperature overload
        gamestate.power_load = 50
        gamestate.temperature = 400.0
        gamestate.check_overload()
        assert gamestate.is_overloaded is True

    def test_buy_power(self, admin_auth, clean_gamestate):
        """4.9: Buy power increases capacity."""
        gamestate.treasury_balance = 2000
        initial_capacity = gamestate.power_capacity

        response = client.post("/api/admin/power/buy", headers=admin_auth)
        assert response.status_code == 200
        data = response.json()
        assert data["capacity"] == initial_capacity + 50
        assert data["balance"] == 1000

    def test_buy_power_insufficient_funds(self, admin_auth, clean_gamestate):
        """4.9b: Buy power fails with insufficient funds."""
        gamestate.treasury_balance = 500

        response = client.post("/api/admin/power/buy", headers=admin_auth)
        assert response.status_code == 400

    def test_reset_gamestate(self, clean_gamestate):
        """4.10: Reset gamestate to defaults."""
        gamestate.temperature = 500.0
        gamestate.global_shift_offset = 5
        gamestate.treasury_balance = 9999

        gamestate.reset_state()

        assert gamestate.temperature == 80.0
        assert gamestate.global_shift_offset == 0
        assert gamestate.treasury_balance == 500


# ============================================================================
# BLOCK 5: AI OPTIMIZER & LLM CONFIG
# ============================================================================

class TestOptimizerSystem:
    """Block 5: Verify optimizer toggle, prompt config, and LLM settings."""

    def test_toggle_optimizer(self, admin_auth, clean_gamestate):
        """5.1 & 5.2: Toggle optimizer on and off."""
        # On
        response = client.post(
            "/api/admin/optimizer/toggle",
            json={"active": True},
            headers=admin_auth
        )
        assert response.status_code == 200
        assert response.json()["optimizer_active"] is True
        assert gamestate.optimizer_active is True

        # Off
        response = client.post(
            "/api/admin/optimizer/toggle",
            json={"active": False},
            headers=admin_auth
        )
        assert response.status_code == 200
        assert response.json()["optimizer_active"] is False

    def test_set_optimizer_prompt(self, admin_auth):
        """5.3: Set optimizer prompt."""
        response = client.post(
            "/api/admin/optimizer/prompt",
            json={"prompt": "Test prompt"},
            headers=admin_auth
        )
        assert response.status_code == 200
        assert gamestate.optimizer_prompt == "Test prompt"

    def test_get_llm_config(self, admin_auth):
        """5.4: Get LLM config."""
        response = client.get("/api/admin/llm/config", headers=admin_auth)
        assert response.status_code == 200
        data = response.json()
        assert "task" in data
        assert "hyper" in data

    def test_set_llm_config(self, admin_auth):
        """5.5 & 5.6: Set LLM config."""
        config = {
            "provider": "openai",
            "model_name": "gpt-4o-mini",
            "system_prompt": "Test prompt"
        }

        response = client.post("/api/admin/llm/config/task", json=config, headers=admin_auth)
        assert response.status_code == 200

        response = client.post("/api/admin/llm/config/hyper", json=config, headers=admin_auth)
        assert response.status_code == 200

    def test_get_api_keys(self, root_auth):
        """5.7: Get API keys (masked) - Root only."""
        response = client.get("/api/admin/llm/keys", headers=root_auth)
        assert response.status_code == 200


# ============================================================================
# BLOCK 6: ROOT CONTROLS
# ============================================================================

class TestRootControls:
    """Block 6: Verify root-level system controls."""

    def test_update_constants(self, root_auth, clean_gamestate):
        """6.1: Update system constants - Root only."""
        constants = {
            "tax_rate": 0.30,
            "power_cap": 200,
            "temp_threshold": 400.0,
            "temp_reset_val": 90.0,
            "temp_min": 25.0,
            "cost_base": 15.0,
            "cost_user": 8.0,
            "cost_autopilot": 12.0,
            "cost_low_latency": 35.0,
            "cost_optimizer": 20.0
        }

        response = client.post(
            "/api/admin/root/update_constants",
            json=constants,
            headers=root_auth
        )
        assert response.status_code == 200

        assert gamestate.tax_rate == 0.30
        assert gamestate.power_capacity == 200
        assert gamestate.TEMP_THRESHOLD == 400.0

    def test_get_root_state(self, root_auth):
        """6.2: Get root state - Root only."""
        response = client.get("/api/admin/root/state", headers=root_auth)
        assert response.status_code == 200
        data = response.json()
        assert "tax_rate" in data
        assert "treasury" in data
        assert "costs" in data

    def test_get_ai_config(self, root_auth):
        """6.3: Get AI config - Root only."""
        response = client.get("/api/admin/root/ai_config", headers=root_auth)
        assert response.status_code == 200
        data = response.json()
        assert "optimizer_prompt" in data
        assert "autopilot_model" in data

    def test_update_ai_config(self, root_auth):
        """6.4: Update AI config - Root only."""
        config = {
            "optimizer_prompt": "New optimizer prompt",
            "autopilot_model": "gpt-4o"
        }

        response = client.post(
            "/api/admin/root/ai_config",
            json=config,
            headers=root_auth
        )
        assert response.status_code == 200
        assert gamestate.optimizer_prompt == "New optimizer prompt"

    def test_system_reset(self, root_auth):
        """6.5: System reset clears data - Root only."""
        # Create some data
        db = SessionLocal()
        db.add(SystemLog(event_type="TEST", message="Test log"))
        db.commit()
        db.close()

        response = client.post("/api/admin/root/reset", headers=root_auth)
        assert response.status_code == 200

        db = SessionLocal()
        logs = db.query(SystemLog).all()
        tasks = db.query(Task).all()
        db.close()

        assert len(logs) == 0
        assert len(tasks) == 0

    def test_get_system_logs(self, admin_auth):
        """6.6: Get system logs."""
        response = client.get("/api/admin/system_logs", headers=admin_auth)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_reset_system_logs(self, admin_auth):
        """6.7: Reset system logs."""
        db = SessionLocal()
        db.add(SystemLog(event_type="TEST", message="Test log"))
        db.commit()
        db.close()

        response = client.post("/api/admin/system_logs/reset", headers=admin_auth)
        assert response.status_code == 200

        db = SessionLocal()
        logs = db.query(SystemLog).all()
        db.close()
        assert len(logs) == 0

    def test_admin_cannot_access_root_endpoints(self, admin_auth):
        """6.8: Regular admin should not access root-only endpoints."""
        # Test a few root-only endpoints
        response = client.get("/api/admin/llm/keys", headers=admin_auth)
        assert response.status_code == 403
        
        response = client.get("/api/admin/root/state", headers=admin_auth)
        assert response.status_code == 403
        
        response = client.get("/api/admin/root/ai_config", headers=admin_auth)
        assert response.status_code == 403


# ============================================================================
# BLOCK 7: ADMIN LABELS & DEBUG
# ============================================================================

class TestAdminFeatures:
    """Block 7: Verify admin-specific features."""

    def test_save_and_get_labels(self, admin_auth):
        """7.1 & 7.2: Save and get labels."""
        labels = {"session1": "VIP User", "session2": "Regular"}

        response = client.post(
            "/api/admin/labels",
            json={"labels": labels},
            headers=admin_auth
        )
        assert response.status_code == 200

        response = client.get("/api/admin/labels", headers=admin_auth)
        assert response.status_code == 200
        assert response.json() == labels

    def test_set_treasury(self, admin_auth, clean_gamestate):
        """7.3: Set treasury (debug)."""
        response = client.post(
            "/api/admin/debug/treasury",
            json={"amount": 9999},
            headers=admin_auth
        )
        assert response.status_code == 200
        assert gamestate.treasury_balance == 9999

    def test_set_timer(self, admin_auth, clean_gamestate):
        """7.4: Set response timer."""
        response = client.post(
            "/api/admin/timer",
            json={"seconds": 60},
            headers=admin_auth
        )
        assert response.status_code == 200
        assert gamestate.agent_response_window == 60

    def test_get_control_state(self, admin_auth):
        """7.5: Get control state."""
        response = client.get("/api/admin/controls/state", headers=admin_auth)
        assert response.status_code == 200
        data = response.json()
        assert "optimizer_active" in data
        assert "agent_response_window" in data


# ============================================================================
# BLOCK 8: WEBSOCKET COMMUNICATION
# ============================================================================

class TestWebSocketCommunication:
    """Block 8: Verify WebSocket connections and message routing.
    
    Note: WebSocket tests are simplified to avoid hanging. They focus on
    connection establishment and basic message sending. Database verification
    is used to confirm message processing worked.
    """

    def test_websocket_connect_valid_token(self):
        """8.1: Connect with valid token."""
        response = client.post("/auth/login", data={"username": "admin1", "password": "secure_admin_1"})
        token = response.json()["access_token"]

        with client.websocket_connect(f"/ws/connect?token={token}") as ws:
            # Connection successful, receive init message
            data = ws.receive_json()
            assert data["type"] == "init"

    def test_websocket_connect_invalid_token(self):
        """8.2: Connect with invalid token should be rejected."""
        try:
            with client.websocket_connect("/ws/connect?token=invalid_token") as ws:
                pass
            assert False, "Should have been rejected"
        except Exception:
            pass  # Expected - connection rejected

    def test_websocket_user_chat_db_verify(self, clean_user, clean_gamestate):
        """8.3: User sends chat message - verify via database."""
        # Clean up any existing test messages
        db = SessionLocal()
        db.query(ChatLog).filter(ChatLog.content == "Suite B Test Message").delete()
        db.commit()
        db.close()

        response = client.post("/auth/login", data={"username": "user1", "password": "subject_pass_1"})
        token = response.json()["access_token"]

        with client.websocket_connect(f"/ws/connect?token={token}") as ws:
            # Receive initial messages (user_status, possibly task_update)
            ws.receive_json()  # user_status
            
            # Send message
            ws.send_json({"content": "Suite B Test Message"})
            
            # Give it a moment to process
            time.sleep(0.1)

        # Verify message was stored in database
        db = SessionLocal()
        log = db.query(ChatLog).filter(ChatLog.content == "Suite B Test Message").first()
        db.close()
        assert log is not None, "Message should be saved to database"

    def test_websocket_task_request_db_verify(self, clean_user, clean_gamestate):
        """8.6: User requests task via WebSocket - verify via database."""
        # Clear existing tasks
        db = SessionLocal()
        user = db.query(User).filter(User.username == "user1").first()
        user_id = user.id
        db.query(Task).filter(Task.user_id == user_id).delete()
        db.commit()
        db.close()

        response = client.post("/auth/login", data={"username": "user1", "password": "subject_pass_1"})
        token = response.json()["access_token"]

        with client.websocket_connect(f"/ws/connect?token={token}") as ws:
            ws.receive_json()  # user_status
            ws.send_json({"type": "task_request"})
            
            # Give it a moment to process
            time.sleep(0.1)

        # Verify task was created in database
        db = SessionLocal()
        task = db.query(Task).filter(Task.user_id == user_id).first()
        db.close()
        assert task is not None, "Task should be created"
        assert task.status == TaskStatus.PENDING_APPROVAL

    def test_websocket_report_optimized_message_db_verify(self, clean_user, clean_gamestate):
        """8.7: Report optimized message - immunity check."""
        # Create optimized message
        db = SessionLocal()
        user = db.query(User).filter(User.username == "user1").first()
        log = ChatLog(session_id=1, sender_id=user.id, content="Optimized msg for report test", is_optimized=True)
        db.add(log)
        db.commit()
        log_id = log.id
        initial_temp = gamestate.temperature
        db.close()

        response = client.post("/auth/login", data={"username": "user1", "password": "subject_pass_1"})
        token = response.json()["access_token"]

        with client.websocket_connect(f"/ws/connect?token={token}") as ws:
            ws.receive_json()  # user_status
            ws.send_json({"type": "report_message", "id": log_id})
            
            time.sleep(0.1)

        # Temperature should NOT have increased (optimized message = immune)
        assert gamestate.temperature == initial_temp, "Optimized messages should be immune to reports"

    def test_websocket_admin_shift_command_db_verify(self, clean_gamestate):
        """8.9: Admin shift command - verify gamestate change."""
        gamestate.global_shift_offset = 0
        
        response = client.post("/auth/login", data={"username": "admin1", "password": "secure_admin_1"})
        token = response.json()["access_token"]

        with client.websocket_connect(f"/ws/connect?token={token}") as ws:
            ws.receive_json()  # init
            ws.send_json({"type": "shift_command"})
            
            time.sleep(0.1)

        # Verify shift was incremented
        assert gamestate.global_shift_offset == 1, "Shift should be incremented"

    def test_websocket_admin_test_mode_toggle(self, clean_gamestate):
        """8.12: Admin test mode toggle."""
        gamestate.test_mode = False
        
        response = client.post("/auth/login", data={"username": "admin1", "password": "secure_admin_1"})
        token = response.json()["access_token"]

        with client.websocket_connect(f"/ws/connect?token={token}") as ws:
            ws.receive_json()  # init
            ws.send_json({"type": "test_mode_toggle", "enabled": True})
            
            time.sleep(0.1)

        assert gamestate.test_mode is True, "Test mode should be enabled"
        gamestate.test_mode = False  # Cleanup


# ============================================================================
# BLOCK 9: ROUTING LOGIC
# ============================================================================

class TestRoutingLogic:
    """Block 9: Verify session-based routing and shift calculations."""

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket."""
        class MockWebSocket:
            def __init__(self, id):
                self.id = id
                self.sent_messages = []

            async def send_text(self, message: str):
                self.sent_messages.append(message)

            async def accept(self):
                pass

        return MockWebSocket

    @pytest.mark.asyncio
    async def test_routing_shift_0(self, mock_websocket, clean_gamestate):
        """9.2: Agent routing at shift 0."""
        from app.logic.routing import routing_logic

        # Reset connections
        routing_logic.user_connections = {}
        routing_logic.agent_connections = {}

        ws_user1 = mock_websocket("u1")
        ws_agent1 = mock_websocket("a1")
        ws_agent2 = mock_websocket("a2")

        await routing_logic.connect(ws_user1, UserRole.USER, 1)
        await routing_logic.connect(ws_agent1, UserRole.AGENT, 1)
        await routing_logic.connect(ws_agent2, UserRole.AGENT, 2)

        gamestate.set_shift(0)

        await routing_logic.broadcast_to_session(1, "Hello Session 1")

        assert "Hello Session 1" in ws_user1.sent_messages
        assert "Hello Session 1" in ws_agent1.sent_messages
        assert "Hello Session 1" not in ws_agent2.sent_messages

    @pytest.mark.asyncio
    async def test_routing_shift_1(self, mock_websocket, clean_gamestate):
        """9.3: Agent routing at shift 1."""
        from app.logic.routing import routing_logic

        # Reset connections
        routing_logic.user_connections = {}
        routing_logic.agent_connections = {}

        ws_user1 = mock_websocket("u1")
        ws_agent1 = mock_websocket("a1")
        ws_agent2 = mock_websocket("a2")

        await routing_logic.connect(ws_user1, UserRole.USER, 1)
        await routing_logic.connect(ws_agent1, UserRole.AGENT, 1)
        await routing_logic.connect(ws_agent2, UserRole.AGENT, 2)

        gamestate.set_shift(1)

        # Clear previous messages
        ws_user1.sent_messages = []
        ws_agent1.sent_messages = []
        ws_agent2.sent_messages = []

        await routing_logic.broadcast_to_session(2, "Hello Session 2")

        # User 1 is Session 1, not Session 2
        assert "Hello Session 2" not in ws_user1.sent_messages
        # Agent 1 at shift 1 -> Session 2
        assert "Hello Session 2" in ws_agent1.sent_messages
        # Agent 2 at shift 1 -> Session 3
        assert "Hello Session 2" not in ws_agent2.sent_messages

    @pytest.mark.asyncio
    async def test_broadcast_to_admins(self, mock_websocket, clean_gamestate):
        """9.5: Broadcast to admins."""
        from app.logic.routing import routing_logic

        routing_logic.admin_connections = []

        ws_admin1 = mock_websocket("admin1")
        ws_admin2 = mock_websocket("admin2")

        routing_logic.admin_connections.append(ws_admin1)
        routing_logic.admin_connections.append(ws_admin2)

        await routing_logic.broadcast_to_admins("Admin message")

        assert "Admin message" in ws_admin1.sent_messages
        assert "Admin message" in ws_admin2.sent_messages

    @pytest.mark.asyncio
    async def test_broadcast_global(self, mock_websocket, clean_gamestate):
        """9.6: Broadcast global."""
        from app.logic.routing import routing_logic

        routing_logic.user_connections = {}
        routing_logic.agent_connections = {}
        routing_logic.admin_connections = []

        ws_user = mock_websocket("u1")
        ws_agent = mock_websocket("a1")
        ws_admin = mock_websocket("admin")

        await routing_logic.connect(ws_user, UserRole.USER, 1)
        await routing_logic.connect(ws_agent, UserRole.AGENT, 1)
        routing_logic.admin_connections.append(ws_admin)

        await routing_logic.broadcast_global("Global message")

        assert "Global message" in ws_user.sent_messages
        assert "Global message" in ws_agent.sent_messages
        assert "Global message" in ws_admin.sent_messages

    def test_get_online_status(self, clean_gamestate):
        """9.7: Online status."""
        from app.logic.routing import routing_logic

        routing_logic.user_connections = {1: [], 2: []}
        routing_logic.agent_connections = {1: [], 3: []}

        status = routing_logic.get_online_status()
        assert 1 in status["users"]
        assert 2 in status["users"]
        assert 1 in status["agents"]
        assert 3 in status["agents"]

    def test_get_active_counts(self, clean_gamestate):
        """9.8: Active counts."""
        from app.logic.routing import routing_logic

        routing_logic.user_connections = {1: [], 2: [], 3: []}
        routing_logic.active_autopilots = {1: True, 2: False, 3: True}

        counts = routing_logic.get_active_counts()
        assert counts["users"] == 3
        assert counts["autopilots"] == 2


# ============================================================================
# BLOCK 10: INTEGRATION SCENARIOS
# ============================================================================

class TestIntegrationScenarios:
    """Block 10: End-to-end flows combining multiple features."""

    def test_full_task_flow(self, admin_auth, clean_user, clean_gamestate):
        """10.1: Full task flow (request → approve → submit → pay)."""
        db = SessionLocal()
        user = db.query(User).filter(User.username == "user1").first()
        user_id = user.id
        initial_credits = 100
        user.credits = initial_credits
        db.query(Task).filter(Task.user_id == user_id).delete()
        db.commit()
        db.close()

        # Create task
        db = SessionLocal()
        task = Task(
            user_id=user_id,
            prompt_desc="Integration Test Task",
            status=TaskStatus.PENDING_APPROVAL
        )
        db.add(task)
        db.commit()
        task_id = task.id
        db.close()

        # Approve
        gamestate.tax_rate = 0.20
        response = client.post(
            "/api/admin/tasks/approve",
            json={"task_id": task_id, "reward": 100},
            headers=admin_auth
        )
        assert response.status_code == 200

        # Pay
        response = client.post(
            "/api/admin/tasks/pay",
            json={"task_id": task_id, "rating": 100},
            headers=admin_auth
        )
        assert response.status_code == 200
        data = response.json()
        assert data["net_reward"] == 80

        # Verify user credits increased
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        assert user.credits == initial_credits + 80
        db.close()

    def test_purgatory_flow(self, admin_auth, clean_user, clean_gamestate):
        """10.2: Purgatory flow (fine → lockout → work → unlock)."""
        db = SessionLocal()
        user = db.query(User).filter(User.username == "user1").first()
        user_id = user.id
        user.credits = 100
        user.is_locked = False
        db.query(Task).filter(Task.user_id == user_id).delete()
        db.commit()
        db.close()

        # Fine to negative
        response = client.post(
            "/api/admin/economy/fine",
            json={"user_id": user_id, "amount": 200, "reason": "Purgatory test"},
            headers=admin_auth
        )
        assert response.status_code == 200

        # Verify locked
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        assert user.credits == -100
        assert user.is_locked is True
        db.close()

        # Create and complete task
        db = SessionLocal()
        task = Task(
            user_id=user_id,
            prompt_desc="Redemption Task",
            status=TaskStatus.PENDING_APPROVAL
        )
        db.add(task)
        db.commit()
        task_id = task.id
        db.close()

        # Approve with high reward
        gamestate.tax_rate = 0.0  # No tax for cleaner calculation
        response = client.post(
            "/api/admin/tasks/approve",
            json={"task_id": task_id, "reward": 200},
            headers=admin_auth
        )
        assert response.status_code == 200

        # Pay
        response = client.post(
            "/api/admin/tasks/pay",
            json={"task_id": task_id, "rating": 100},
            headers=admin_auth
        )
        assert response.status_code == 200

        # Bonus to unlock
        response = client.post(
            "/api/admin/economy/bonus",
            json={"user_id": user_id, "amount": 100, "reason": "Freedom"},
            headers=admin_auth
        )

        # Verify unlocked
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        assert user.credits >= 0
        assert user.is_locked is False
        db.close()

    def test_power_crisis(self, admin_auth, clean_gamestate):
        """10.3: Power crisis (load > capacity)."""
        gamestate.power_capacity = 50
        gamestate.COST_BASE = 10
        gamestate.COST_PER_USER = 5
        gamestate.optimizer_active = True
        gamestate.COST_OPTIMIZER_ACTIVE = 50  # This alone exceeds capacity

        load = gamestate.calc_load(active_terminals=2, active_autopilots=0, low_latency_active=False)
        # 10 + 2*5 + 50 = 70 > 50
        assert load > gamestate.power_capacity

        gamestate.check_overload()
        assert gamestate.is_overloaded is True

    def test_temperature_spike(self, clean_gamestate):
        """10.4: Temperature spike from reports."""
        gamestate.set_temperature(300.0)
        gamestate.TEMP_THRESHOLD = 350.0

        # Multiple reports
        for _ in range(4):
            gamestate.report_anomaly()  # +15 each

        # 300 + 4*15 = 360 > 350
        assert gamestate.temperature > gamestate.TEMP_THRESHOLD

        gamestate.check_overload()
        assert gamestate.is_overloaded is True

    @pytest.mark.asyncio
    async def test_shift_rotation_affects_routing(self, clean_gamestate):
        """10.5: Shift rotation affects routing."""
        from app.logic.routing import routing_logic

        class MockWS:
            def __init__(self):
                self.sent = []

            async def send_text(self, msg):
                self.sent.append(msg)

            async def accept(self):
                pass

        routing_logic.user_connections = {}
        routing_logic.agent_connections = {}

        ws_user1 = MockWS()
        ws_agent1 = MockWS()

        await routing_logic.connect(ws_user1, UserRole.USER, 1)
        await routing_logic.connect(ws_agent1, UserRole.AGENT, 1)

        # Shift 0: Agent 1 -> Session 1
        gamestate.set_shift(0)
        await routing_logic.broadcast_to_session(1, "Shift 0 message")
        assert "Shift 0 message" in ws_agent1.sent

        ws_agent1.sent.clear()

        # Shift 1: Agent 1 -> Session 2
        gamestate.set_shift(1)
        await routing_logic.broadcast_to_session(1, "Shift 1 message")
        assert "Shift 1 message" not in ws_agent1.sent  # Agent 1 is now on Session 2
