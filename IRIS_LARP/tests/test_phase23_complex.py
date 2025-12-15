
import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, User, Task, TaskStatus, ChatLog, SystemLog, UserRole
from app.logic.gamestate import gamestate
import json

client = TestClient(app)

class TestPhase23Complex(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize DB explicitly
        from app.database import init_db
        init_db()
        
        # Ensure users exist
        from app.seed import seed_data
        seed_data()
            
        # Reset State manually first
        gamestate.reset_state()
        
        # Mock LLM
        from unittest.mock import AsyncMock
        from app.logic.llm_core import llm_service
        llm_service.rewrite_message = AsyncMock(return_value="REWRITTEN CONTENT")

    def get_auth_token(self, username, password):
        response = client.post("/auth/login", data={"username": username, "password": password})
        self.assertEqual(response.status_code, 200)
        return response.json()["access_token"]

    def get_auth_headers(self, username, password):
        token = self.get_auth_token(username, password)
        return {"Authorization": f"Bearer {token}"}

    def test_optimizer_confirm_flow(self):
        # 1. Turn Optimizer ON
        admin_auth = self.get_auth_headers("admin1", "secure_admin_1")
        res = client.post("/api/admin/optimizer/toggle", json={"active": True}, headers=admin_auth)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(gamestate.optimizer_active)
        
        # 2. Agent Connects
        token = self.get_auth_token("agent1", "agent_pass_1")
        
        with client.websocket_connect(f"/ws/connect?token={token}") as ws:
            # Drain Init Messages
            while True:
                # We expect history etc.
                # Just peek until we get passed init?
                # Actually, easier to just send immediately and ignore responses until ours?
                # But we need to catch 'optimizer_preview'.
                # Let's read until timeout or empty?
                # TestClient WS buffer might hold messages.
                # Let's send a message and read responses.
                
                # Send Message
                ws.send_json({"content": "Test Message Raw"})
                
                found_preview = False
                preview_data = {}
                
                # Read loop
                for _ in range(10): # Max attempts
                    data = ws.receive_json()
                    # Skip init/history
                    if data.get("type") == "optimizer_preview":
                        found_preview = True
                        preview_data = data
                        break
                    if data.get("type") == "optimizing_start":
                        continue # Expected
                
                if not found_preview:
                    self.fail("Did not receive optimizer_preview")
                
                self.assertEqual(preview_data["original"], "Test Message Raw")
                self.assertIn("rewritten", preview_data)
                rewritten = preview_data["rewritten"]
                
                # 3. Confirm
                ws.send_json({"content": rewritten, "confirm_opt": True})
                
                # 4. Expect Echo (Broadcast)
                found_broadcast = False
                for _ in range(5):
                    data = ws.receive_json()
                    if data.get("role") == "agent" and data.get("content") == rewritten:
                        found_broadcast = True
                        break
                
                self.assertTrue(found_broadcast, "Did not receive broadcast of confirmed message")
                break

    def test_task_edit_on_approve(self):
        admin_auth = self.get_auth_headers("admin1", "secure_admin_1")
        
        # Create Task (Manual DB)
        db = SessionLocal()
        u = db.query(User).filter(User.username == "user1").first()
        t = Task(user_id=u.id, prompt_desc="Original Prompt", status=TaskStatus.PENDING_APPROVAL)
        db.add(t)
        db.commit()
        tid = t.id
        db.close()
        
        # Approve with Edit
        res = client.post("/api/admin/tasks/approve", 
                          json={"task_id": tid, "reward": 500, "prompt_content": "EDITED PROMPT"},
                          headers=admin_auth)
        self.assertEqual(res.status_code, 200)
        
        # Verify DB
        db = SessionLocal()
        t = db.query(Task).filter(Task.id == tid).first()
        self.assertEqual(t.status, TaskStatus.ACTIVE)
        self.assertEqual(t.prompt_desc, "EDITED PROMPT")
        db.close()

    def test_system_reset(self):
        admin_auth = self.get_auth_headers("admin1", "secure_admin_1") # Assuming admin1 survives reset? 
        # Wait, reset deletes Users?
        # Code: `users = db.query(User).filter(User.role == UserRole.USER).all()`
        # It RESETS credits/locked. It does NOT delete users.
        # It deletes Logs and Tasks.
        
        # Create Dummy Data
        db = SessionLocal()
        db.add(SystemLog(event_type="TEST", message="To match"))
        db.commit()
        
        # Reset
        res = client.post("/api/admin/root/reset", headers=admin_auth)
        self.assertEqual(res.status_code, 200)
        
        # Verify Empty
        db = SessionLocal()
        logs = db.query(SystemLog).all()
        self.assertEqual(len(logs), 0)
        
        tasks = db.query(Task).all()
        self.assertEqual(len(tasks), 0)
        
        u = db.query(User).filter(User.username == "user1").first()
        self.assertEqual(u.credits, 100)
        db.close()

if __name__ == "__main__":
    unittest.main()
