import pytest
import json
from app.logic.gamestate import gamestate
from app.logic.routing import routing_logic
from app.database import UserRole
from app.config import settings


class MockWebSocket:
    def __init__(self, id):
        self.id = id
        self.sent_messages = []

    async def send_text(self, message: str):
        self.sent_messages.append(message)

    async def accept(self):
        pass


@pytest.mark.asyncio
async def test_gamestate_shift():
    gamestate.global_shift_offset = 0
    assert gamestate.global_shift_offset == 0

    gamestate.increment_shift()
    assert gamestate.global_shift_offset == 1

    gamestate.set_shift(settings.TOTAL_SESSIONS - 1)
    assert gamestate.global_shift_offset == 7

    gamestate.increment_shift()
    assert gamestate.global_shift_offset == 0  # wrap around


@pytest.mark.asyncio
async def test_routing_broadcast_to_session():
    # Clean state
    routing_logic.user_connections = {}
    routing_logic.agent_connections = {}
    routing_logic.user_logical_ids = {}
    routing_logic.agent_logical_ids = {}
    gamestate.set_shift(0)

    ws_user1 = MockWebSocket("u1")
    ws_agent1 = MockWebSocket("a1")
    ws_agent2 = MockWebSocket("a2")

    await routing_logic.connect(ws_user1, UserRole.USER, 1, logical_id=1)
    await routing_logic.connect(ws_agent1, UserRole.AGENT, 1, logical_id=1)
    await routing_logic.connect(ws_agent2, UserRole.AGENT, 2, logical_id=2)

    await routing_logic.broadcast_to_session(1, "Hello Session 1")

    assert "Hello Session 1" in ws_user1.sent_messages
    assert "Hello Session 1" in ws_agent1.sent_messages
    assert "Hello Session 1" not in ws_agent2.sent_messages

    # Shift 1: Agent 1 moves to Session 2
    gamestate.set_shift(1)
    ws_user1.sent_messages = []
    ws_agent1.sent_messages = []
    ws_agent2.sent_messages = []

    await routing_logic.broadcast_to_session(2, "Hello Session 2")

    assert "Hello Session 2" not in ws_user1.sent_messages
    assert "Hello Session 2" in ws_agent1.sent_messages
    assert "Hello Session 2" not in ws_agent2.sent_messages

    # Cleanup
    routing_logic.disconnect(ws_user1, UserRole.USER, 1)
    routing_logic.disconnect(ws_agent1, UserRole.AGENT, 1)
    routing_logic.disconnect(ws_agent2, UserRole.AGENT, 2)


@pytest.mark.asyncio
async def test_pending_response_tracking():
    import time

    gamestate.pending_responses = {}
    gamestate.timed_out_sessions = {}
    session_id = 1

    assert session_id not in gamestate.pending_responses
    assert not gamestate.is_session_timed_out(session_id)

    gamestate.start_pending_response(session_id)
    assert session_id in gamestate.pending_responses

    gamestate.clear_pending_response(session_id)
    assert session_id not in gamestate.pending_responses

    gamestate.start_pending_response(session_id)
    gamestate.mark_session_timeout(session_id)
    assert session_id not in gamestate.pending_responses
    assert gamestate.is_session_timed_out(session_id)

    gamestate.clear_session_timeout(session_id)
    assert not gamestate.is_session_timed_out(session_id)


def test_panic_mode_state_toggle():
    gamestate.panic_modes = {}
    session_id = 2

    state = gamestate.get_panic_state(session_id)
    assert state["user"] is False and state["agent"] is False

    gamestate.set_panic_mode(session_id, "user", True)
    state = gamestate.get_panic_state(session_id)
    assert state["user"] is True and state["agent"] is False

    gamestate.set_panic_mode(session_id, "agent", True)
    state = gamestate.get_panic_state(session_id)
    assert state["user"] is True and state["agent"] is True

    gamestate.clear_panic_state(session_id)
    state = gamestate.get_panic_state(session_id)
    assert state["user"] is False and state["agent"] is False


@pytest.mark.asyncio
async def test_timeout_error_sent_to_user():
    routing_logic.user_connections = {}
    routing_logic.user_logical_ids = {}

    ws_user1 = MockWebSocket("u1")
    await routing_logic.connect(ws_user1, UserRole.USER, 1, logical_id=1)

    await routing_logic.send_timeout_error_to_user(1)

    assert len(ws_user1.sent_messages) == 1
    msg = json.loads(ws_user1.sent_messages[0])
    assert msg["type"] == "agent_timeout"

    routing_logic.disconnect(ws_user1, UserRole.USER, 1)
