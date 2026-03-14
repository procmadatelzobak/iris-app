
import requests
import json
import logging
import time

# Config
BASE_URL = "http://localhost:8000"
ADMIN_USER = "admin1"
ADMIN_PASS = "secure_admin_1" 
USER_USER = "user1"
USER_PASS = "subject_pass_1"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_token(username, password):
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", data={"username": username, "password": password})
        if resp.status_code != 200:
            logger.error(f"Login failed for {username}: {resp.text}")
            return None
        return resp.json()["access_token"]
    except Exception as e:
        logger.error(f"Connection Failed: {e}")
        return None

def run_verification():
    logger.info("--- STARTING v1.5 OPTIMIZER VERIFICATION ---")

    # 1. Login
    admin_token = get_token(ADMIN_USER, ADMIN_PASS)
    if not admin_token:
        logger.error("Auth failed - Is Server Running?")
        return
        
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Check Economy Defaults (Treasury should be > 0, likely 500 if reset)
    # We can use the debug endpoint or check via side channel. 
    # Or just try to buy power (requires 1000). 500 is insufficient.
    # Let's check via Buy Power response (it returns balance).
    # Buying fails, but returns message? No, returns 400.
    # We'll use the debug endpoint to READ (Set to current val? No).
    # We'll rely on a task payment to see balance increment.
    
    # 3. Test Optimizer API
    logger.info("--- Testing Optimizer API ---")
    
    # 3.1 Toggle
    resp = requests.post(f"{BASE_URL}/api/admin/optimizer/toggle", json={"active": True}, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["optimizer_active"] == True
    logger.info("Optimizer Enabled: OK")
    
    # 3.2 Prompt
    resp = requests.post(f"{BASE_URL}/api/admin/optimizer/prompt", json={"prompt": "TEST MODE"}, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["optimizer_prompt"] == "TEST MODE"
    logger.info("Optimizer Prompt Set: OK")
    
    # 4. Test Economy (Task Pay)
    logger.info("--- Testing Economy Logic ---")
    
    # Seed Task
    from app.database import SessionLocal, Task, TaskStatus, User
    db = SessionLocal()
    u = db.query(User).filter(User.username == USER_USER).first()
    t = Task(user_id=u.id, prompt_desc="Eco Test", reward_offered=1000, status=TaskStatus.SUBMITTED, submission_content="Done")
    db.add(t)
    db.commit()
    task_id = t.id
    logger.info(f"Seeded Task {task_id}")
    
    # Pay Task
    pay_payload = {"task_id": task_id, "rating": 100}
    # This calls the new Refactored endpoint
    resp = requests.post(f"{BASE_URL}/api/admin/tasks/pay", json=pay_payload, headers=admin_headers)
    logger.info(f"Pay Resp: {resp.text}")
    assert resp.status_code == 200
    data = resp.json()
    
    # Check v1.5 Tax Logic (20%)
    # Reward 1000 -> Tax 200 -> Net 800
    assert data["tax_collected"] == 200
    assert data["net_reward"] == 800
    logger.info("Tax Logic (20%): OK")
    
    db.close()
    
    logger.info("--- v1.5 VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    run_verification()
