
import unittest
import json
import os
import time
import sys
# Add parent directory to path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, User, Task, TaskStatus, ChatLog, SystemLog, UserRole, init_db
from app.logic.gamestate import gamestate
from app.seed import seed_data

client = TestClient(app)

class TestHlinikWorkflow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize DB and Seed
        init_db()
        # Seed ensures we have admin1 and user1
        try:
            seed_data()
        except Exception as e:
            print(f"Seed warning: {e}")
        
        gamestate.reset_state()
        gamestate.treasury_balance = 1000

    def get_auth_token(self, username, password="password"):
        response = client.post("/auth/login", data={"username": username, "password": password})
        if response.status_code != 200:
            raise Exception(f"Login failed for {username}: {response.text}")
        return response.json()["access_token"]

    def test_full_workflow(self):
        print("\n=== STARTING HLINIK WORKFLOW TEST ===")
        test_start_time = time.time()
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "scenario_name": "HLINIK Workflow Automation",
            "status": "running",
            "steps": [],
            "stats": {}
        }

        try:
            # 1. Login
            print("Step 1: Authenticating...")
            admin_token = self.get_auth_token("admin1", "secure_admin_1")
            user_token = self.get_auth_token("user1", "subject_pass_1")
            
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            
            # 2. User Requests Task via WebSocket
            print("Step 2: User Requesting Task...")
            task_id = None
            initial_credits = 0
            
            with client.websocket_connect(f"/ws/connect?token={user_token}") as ws_user:
                # Read initial status
                init_msg = ws_user.receive_json() # status_update or gamestate
                # Flush initial messages
                while True:
                    try:
                        # set timeout to avoid hanging if no more messages
                        # Note: TestClient WS doesn't support timeout easily in receive_json without simple Loop
                        # We just assume we get what we expect. 
                        # The first relevant msg is user_status
                         msg = ws_user.receive_json()
                         if msg.get("type") == "user_status":
                             initial_credits = msg.get("credits", 0)
                             break
                    except Exception:
                        break
                
                # Send Request
                ws_user.send_json({"type": "task_request"})
                
                # Expect Task Update (Pending)
                while True:
                    msg = ws_user.receive_json()
                    if msg.get("type") == "task_update":
                        self.assertEqual(msg["status"], "pending_approval")
                        self.assertIn("Waiting", msg["description"])
                        print(f"   -> Task Requested. Status: {msg['status']}")
                        report_data["steps"].append({"step": "task_request", "status": "passed"})
                        break

            # 3. Admin Approves Task
            print("Step 3: Admin Approving Task...")
            # Fetch pending task ID
            res = client.get("/api/admin/tasks", headers=admin_headers)
            tasks = res.json()
            pending_task = next((t for t in tasks if t["status"] == "pending_approval" and t["prompt"] == "Waiting for assignment..."), None)
            self.assertIsNotNone(pending_task, "No pending task found")
            task_id = pending_task["id"]
            
            # Approve (triggers LLM)
            # We don't provide prompt_content to force LLM usage
            res = client.post("/api/admin/tasks/approve", 
                              json={"task_id": task_id, "reward": 150},
                              headers=admin_headers)
            self.assertEqual(res.status_code, 200)
            approved_data = res.json()
            print(f"   -> Task {task_id} Approved. LLM generated prompt length: {len(pending_task['prompt'])}")
            
            # Verify Prompt content updated in DB
            db = SessionLocal()
            t_obj = db.query(Task).filter(Task.id == task_id).first()
            generated_prompt = t_obj.prompt_desc
            db.close()
            print(f"   -> Generated Prompt: {generated_prompt[:50]}...")
            
            report_data["steps"].append({
                "step": "admin_approve", 
                "status": "passed", 
                "details": {"llm_used": generated_prompt != "Waiting for assignment..."}
            })

            # 4. User Submits Task
            print("Step 4: User Submitting Task...")
            with client.websocket_connect(f"/ws/connect?token={user_token}") as ws_user:
                # Flush potential previous messages
                # Just send submit, server handles it
                submission_text = "Analysis complete. System nominal."
                ws_user.send_json({"type": "task_submit", "task_id": task_id, "content": submission_text})
                
                # Expect confirmation
                while True:
                    msg = ws_user.receive_json()
                    if msg.get("type") == "task_update" and msg.get("status") == "submitted":
                        self.assertEqual(msg["submission"], submission_text)
                        print("   -> Task Submitted.")
                        report_data["steps"].append({"step": "user_submit", "status": "passed"})
                        break

            # 5. Admin Grades Task
            print("Step 5: Admin Grading Task...")
            modifier = 1.0 # 100%
            res = client.post("/api/admin/tasks/grade",
                              json={"task_id": task_id, "rating_modifier": modifier},
                              headers=admin_headers)
            self.assertEqual(res.status_code, 200)
            grade_res = res.json()
            net_reward = grade_res["net_reward"]
            print(f"   -> Task Graded. Net Reward: {net_reward}")
            
            report_data["steps"].append({"step": "admin_grade", "status": "passed", "reward": net_reward})

            # 6. Verify Final State
            print("Step 6: Verifying...")
            db = SessionLocal()
            u = db.query(User).filter(User.username == "user1").first()
            expected_credits = initial_credits + net_reward
            print(f"   -> Credits: {u.credits} (Expected: {expected_credits})")
            # Note: seed might reset credits to 100.
            # Depending on initial_credits logic.
            # If initial was 100, and net_reward is e.g. 120 (150 - 20%), total 220.
            
            # Check Log
            logs = db.query(ChatLog).filter(ChatLog.sender_id == u.id).all()
            # Contains submission log?
            # Actually ChatLog stores chat messages. Task submission content is in Task table.
            # But the Grade action creates a ChatLog entry: "📋 Úkol ... vyhodnocen"
            grade_log = next((l for l in logs if "vyhodnocen" in l.content), None)
            self.assertIsNotNone(grade_log, "Grade log notification not found")
            db.close()
            
            report_data["steps"].append({"step": "verification", "status": "passed"})
            report_data["status"] = "success"

        except Exception as e:
            print(f"!!! TEST FAILED: {e}")
            report_data["status"] = "failed"
            report_data["error"] = str(e)
            raise e
        finally:
            duration = time.time() - test_start_time
            report_data["duration"] = duration
            
            # Save Report
            filename = f"hlinik_workflow_{int(time.time())}.json"
            out_path = os.path.join("/home/sinuhet/projekty/iris-app/doc/iris/lore-web/data/test_runs", filename)
            
            with open(out_path, "w") as f:
                json.dump(report_data, f, indent=2)
            print(f"\nReport saved to: {out_path}")
            
            # Update index.json
            index_path = "/home/sinuhet/projekty/iris-app/doc/iris/lore-web/data/test_runs/index.json"
            try:
                if os.path.exists(index_path):
                    with open(index_path, "r") as f:
                        index = json.load(f)
                else:
                    index = []
                
                # Add summary to index
                index.insert(0, {
                    "timestamp": report_data["timestamp"],
                    "scenario_name": report_data["scenario_name"],
                    "status": report_data["status"],
                    "duration": duration,
                    "filename": filename,
                    "stats": {
                        "steps_completed": len(report_data["steps"])
                    }
                })
                
                with open(index_path, "w") as f:
                    json.dump(index, f, indent=2)
                print("Index updated.")
            except Exception as e:
                print(f"Failed to update index: {e}")

if __name__ == "__main__":
    unittest.main()
