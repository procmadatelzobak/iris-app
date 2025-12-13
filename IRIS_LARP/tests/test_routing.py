import pytest
from app.logic.gamestate import gamestate
from app.config import settings

# Mock WebSocket
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
    # Reset
    gamestate.global_shift_offset = 0
    
    assert gamestate.global_shift_offset == 0
    gamestate.increment_shift()
    assert gamestate.global_shift_offset == 1
    
    gamestate.set_shift(settings.TOTAL_SESSIONS - 1)
    assert gamestate.global_shift_offset == 7
    
    gamestate.increment_shift()
    assert gamestate.global_shift_offset == 0  # Wrap around

@pytest.mark.asyncio
async def test_routing_logic_calculation():
    from app.logic.routing import routing_logic
    
    # Setup: 1 User (ID 1), 2 Agents (ID 1, ID 2)
    # User 1 -> Session 1
    # Agent 1 -> ?
    # Agent 2 -> ?
    
    # Scenario A: Shift 0
    gamestate.set_shift(0)
    
    # Agent 1 (Index 0) + Shift 0 -> Session Index 0 -> Session 1
    # Agent 2 (Index 1) + Shift 0 -> Session Index 1 -> Session 2
    
    # If we broadcast to Session 1, Agent 1 should receive it, Agent 2 should not.
    
    # Mock connections
    ws_user1 = MockWebSocket("u1")
    ws_agent1 = MockWebSocket("a1")
    ws_agent2 = MockWebSocket("a2")
    
    await routing_logic.connect(ws_user1, "user", 1)  # Role check is string vs Enum in real code, be careful
    # In code it uses UserRole enum. Let's import it.
    from app.database import UserRole
    
    # Reset connections for clean test
    routing_logic.user_connections = {}
    routing_logic.agent_connections = {}
    
    await routing_logic.connect(ws_user1, UserRole.USER, 1)
    await routing_logic.connect(ws_agent1, UserRole.AGENT, 1)
    await routing_logic.connect(ws_agent2, UserRole.AGENT, 2)
    
    # Broadcast to Session 1
    await routing_logic.broadcast_to_session(1, "Hello Session 1")
    
    assert "Hello Session 1" in ws_user1.sent_messages
    assert "Hello Session 1" in ws_agent1.sent_messages
    assert "Hello Session 1" not in ws_agent2.sent_messages
    
    # Scenario B: Shift 1
    gamestate.set_shift(1)
    
    # Clear msgs
    ws_user1.sent_messages = []
    ws_agent1.sent_messages = []
    ws_agent2.sent_messages = []
    
    # Agent 1 (Index 0) + Shift 1 -> Session Index 1 -> Session 2
    # Agent 8 (Index 7) + Shift 1 -> Session Index 0 -> Session 1 (Wait, Agent 8?)
    
    # Let's see who is on Session 1 now.
    # We need Agent X such that (X_index + 1) % 8 == 0 (Session Index 0)
    # X_index = -1 -> 7 (Agent 8)
    
    # Let's check Session 2. broadcast to Session 2.
    # User 1 is NOT on Session 2. User 2 would be.
    # Agent 1 should be on Session 2.
    
    await routing_logic.broadcast_to_session(2, "Hello Session 2")
    
    assert "Hello Session 2" not in ws_user1.sent_messages # User 1 is Session 1
    assert "Hello Session 2" in ws_agent1.sent_messages    # Agent 1 is now Session 2
    assert "Hello Session 2" not in ws_agent2.sent_messages # Agent 2 is Session 3
