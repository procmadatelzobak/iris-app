
import asyncio
import sys
import os
import json
from unittest.mock import AsyncMock, MagicMock

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, ChatLog, User, UserRole
from app.services.dispatcher import Dispatcher
from app.logic.gamestate import gamestate

async def verify_architecture():
    print("--- STARTING ARCHITECTURE VERIFICATION ---")
    
    # 1. Setup Database
    db = SessionLocal()
    
    # 2. Setup Dispatcher
    dispatcher = Dispatcher()
    
    # 3. Setup Mocks
    mock_ws = AsyncMock()
    mock_ws.send_text = AsyncMock()
    
    # Create or Get Test User
    test_username = "arch_tester"
    user = db.query(User).filter(User.username == test_username).first()
    if not user:
        user = User(username=test_username, role=UserRole.USER, credits=100)
        db.add(user)
        db.commit()
    
    print(f"[OK] Test User: {user.username} (ID: {user.id})")

    # 4. Simulate Message
    msg_content = "Architecture verification test message."
    msg_data = {
        "type": "chat",
        "content": msg_content
    }
    
    print(f"[INFO] Sending Message: {msg_content}")
    
    try:
        await dispatcher.handle_message(msg_data, user, db, mock_ws)
        print("[OK] Dispatcher handled message without error.")
    except Exception as e:
        print(f"[FAIL] Dispatcher failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # 5. Verify Persistence
    # Check if message is in DB
    log = db.query(ChatLog).filter(ChatLog.content == msg_content).first()
    if log:
        print(f"[OK] Persistence Verified. Message found in DB with ID: {log.id}")
        
        # Cleanup
        db.delete(log)
        db.commit()
        print("[OK] Cleanup complete.")
    else:
        print("[FAIL] Message NOT found in DB.")
    
    # 6. Verify Gamestate Interaction
    # Check if last user message was updated in gamestate
    # Logic in ChatService updates gamestate.latest_user_messages
    # We need to know the logical session ID. For 'arch_tester', it depends on regex or 0.
    # ChatService._get_logical_id returns 0 if no digits.
    # But wait, ChatService creates session 0 logic? 
    # Let's check ChatService logic: "session_id = self._get_logical_id(user.username, 'user')"
    # If username has no digits, session_id is 0.
    
    # Actually, let's update username to have a number to be safe/realistic
    user.username = "arch_tester_99"
    db.commit()
    
    # Retry with valid session ID
    msg_content_2 = "Session 99 test."
    msg_data["content"] = msg_content_2
    
    await dispatcher.handle_message(msg_data, user, db, mock_ws)
    
    session_id = 99
    last_msg = gamestate.get_last_user_message(session_id)
    
    if last_msg == msg_content_2:
         print(f"[OK] GameState Verified. Last message for session {session_id} is correct.")
    else:
         print(f"[FAIL] GameState Mismatch. Expected '{msg_content_2}', got '{last_msg}'")

    db.close()
    print("--- VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(verify_architecture())
