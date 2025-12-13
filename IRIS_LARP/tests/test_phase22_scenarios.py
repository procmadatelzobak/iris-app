
import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, User, Task, TaskStatus, ChatLog, SystemLog, UserRole
from app.logic.gamestate import gamestate

client = TestClient(app)

class TestPhase22(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Ensure users exist
        from app.seed import seed_data
        # Clean DB for verification?
        # seed_data() resets usually? Or creates if missing?
        # We assume seed_data works safely.
        try:
             seed_data()
        except:
             pass 
             
        gamestate.treasury_balance = 1000
        gamestate.power_capacity = 100
        gamestate.temperature = 80.0

    def get_auth_headers(self, username, password="password"):
        response = client.post("/auth/login", data={"username": username, "password": password})
        self.assertEqual(response.status_code, 200)
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_economy_lockout(self):
        admin_auth = self.get_auth_headers("admin1", "secure_admin_1")
        
        # Get User 1 ID
        db = SessionLocal()
        user = db.query(User).filter(User.username == "user1").first()
        self.assertIsNotNone(user, "User1 not found")
        uid = user.id
        user.credits = 10 
        user.is_locked = False
        db.commit()
        db.close()
        
        # Fine -20 (Balance -> -10)
        res = client.post("/api/admin/economy/fine", 
                          json={"user_id": uid, "amount": 20, "reason": "Test Fine"},
                          headers=admin_auth)
        self.assertEqual(res.status_code, 200)
        
        # Verify Locked
        db = SessionLocal()
        u = db.query(User).filter(User.id == uid).first()
        self.assertEqual(u.credits, -10)
        self.assertTrue(u.is_locked)
        db.close()
        
        # Bonus +20 (Balance -> 10)
        res = client.post("/api/admin/economy/bonus", 
                          json={"user_id": uid, "amount": 20, "reason": "Test Bonus"},
                          headers=admin_auth)
                          
        # Verify Unlocked
        db = SessionLocal()
        u = db.query(User).filter(User.id == uid).first()
        self.assertEqual(u.credits, 10)
        self.assertFalse(u.is_locked)
        db.close()

    def test_system_logs(self):
        admin_auth = self.get_auth_headers("admin1", "secure_admin_1")
        # Action: Update Constants (ROOT)
        res = client.post("/api/admin/root/update_constants", 
                          json={
                              "tax_rate": 0.2, "power_cap": 100, 
                              "temp_threshold": 350, "temp_reset_val": 80, "temp_min": 20,
                              "cost_base": 10, "cost_user": 5, "cost_autopilot": 10,
                              "cost_low_latency": 30, "cost_optimizer": 15
                          }, headers=admin_auth)
        self.assertEqual(res.status_code, 200)
        
        # Verify Log
        res_logs = client.get("/api/admin/system_logs", headers=admin_auth)
        logs = res_logs.json()
        self.assertTrue(len(logs) > 0)
        self.assertEqual(logs[0]["event_type"], "ROOT")
        self.assertIn("Constants Updated", logs[0]["message"])

    def test_task_flow(self):
        # Admin Auth
        admin_auth = self.get_auth_headers("admin1", "secure_admin_1")
        
        # 1. Manual Task Create
        db = SessionLocal()
        u = db.query(User).filter(User.username == "user1").first()
        t = Task(user_id=u.id, prompt_desc="Test Task", status=TaskStatus.PENDING_APPROVAL)
        db.add(t)
        db.commit()
        tid = t.id
        db.close()
        
        # 2. Approve
        res = client.post("/api/admin/tasks/approve", json={"task_id": tid, "reward": 100}, headers=admin_auth)
        self.assertEqual(res.status_code, 200)
        
        # 3. Pay
        res = client.post("/api/admin/tasks/pay", json={"task_id": tid, "rating": 100}, headers=admin_auth)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "paid")
        # Logic: 100 Reward, 20% Tax (set in test_system_logs) -> User +80, Treasury +20
        self.assertEqual(data["net_reward"], 80)
        self.assertEqual(data["tax_collected"], 20)

    def test_report_logic(self):
        # Authenticate to get token
        response = client.post("/auth/login", data={"username": "admin1", "password": "secure_admin_1"})
        token = response.json()["access_token"]
        
        with client.websocket_connect(f"/ws/connect?token={token}") as ws:
            # Create Dummy Log
            db = SessionLocal()
            u = db.query(User).filter(User.username == "user1").first()
            log = ChatLog(session_id=1, sender_id=u.id, content="Optimized Msg", is_optimized=True)
            db.add(log)
            db.commit()
            lid = log.id
            db.close()
            
            # Send Report Command
            ws.send_json({"type": "report_message", "id": lid})
            
            # Expect Denial (Skipping broadcasts)
            while True:
                data = ws.receive_json()
                if data.get("type") == "report_denied":
                     self.assertEqual(data["reason"], "SYSTEM_VERIFIED")
                     break
                # Only check first few messages to avoid infinite loop
                if data.get("type") == "error":
                     self.fail("Received Error")

if __name__ == "__main__":
    unittest.main()
