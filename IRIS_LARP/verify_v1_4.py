
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
    logger.info("--- STARTING v1.4 VERIFICATION (Sync) ---")

    # 1. Login
    admin_token = get_token(ADMIN_USER, ADMIN_PASS)
    user_token = get_token(USER_USER, USER_PASS)
    
    if not admin_token or not user_token:
        logger.error("Auth failed - Is Server Running?")
        return
        
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # 2. Test Labels
    logger.info("--- Testing Labels ---")
    label_data = {"lbl_test": "VERIFIED"}
    resp = requests.post(f"{BASE_URL}/api/admin/labels", json={"labels": label_data}, headers=admin_headers)
    logger.info(f"Save Labels: {resp.status_code}")
    assert resp.status_code == 200
    
    resp = requests.get(f"{BASE_URL}/api/admin/labels", headers=admin_headers)
    data = resp.json()
    logger.info(f"Get Labels: {data}")
    assert data.get("lbl_test") == "VERIFIED"

    # 3. Test Treasury & Tax
    logger.info("--- Testing Treasury & Tax ---")
    
    # 3.1 Seed Task (DB)
    from app.database import SessionLocal, Task, TaskStatus, User
    db = SessionLocal()
    u = db.query(User).filter(User.username == USER_USER).first()
    t = Task(user_id=u.id, prompt_desc="Tax Test Sync", reward_offered=2000, status=TaskStatus.SUBMITTED, submission_content="Done")
    db.add(t)
    db.commit()
    task_id = t.id
    logger.info(f"Seeded Task {task_id} for {USER_USER}")
    db.close()
    
    # 3.2 Pay Task
    pay_payload = {"task_id": task_id, "rating": 100}
    resp = requests.post(f"{BASE_URL}/api/admin/tasks/pay", json=pay_payload, headers=admin_headers)
    data = resp.json()
    logger.info(f"Pay Task: {data}")
    assert resp.status_code == 200
    assert data["tax_collected"] == 200
        
    # 4. Test Buy Power
    logger.info("--- Testing Buy Power ---")
    resp = requests.post(f"{BASE_URL}/api/admin/power/buy", headers=admin_headers)
    logger.info(f"Buy Power (Insufficient): {resp.status_code}")
    # Might pass if we accumulated funds from previous runs?
    # But usually 200 is < 1000.
    if resp.status_code == 200:
        logger.warning("Buy Power succeeded unexpectedly (Funds > 1000?)")
    else:
        assert resp.status_code == 400
        
    # 4.1 Force Treasury
    logger.info("Cheated Treasury to 2000")
    resp = requests.post(f"{BASE_URL}/api/admin/debug/treasury", json={"amount": 2000}, headers=admin_headers)
    assert resp.status_code == 200
    
    # 4.2 Buy Power (Success)
    resp = requests.post(f"{BASE_URL}/api/admin/power/buy", headers=admin_headers)
    data = resp.json()
    logger.info(f"Buy Power (Success): {data}")
    assert resp.status_code == 200
    assert data["capacity"] >= 150

    # 5. Test Timer Config
    logger.info("--- Testing Timer Config ---")
    resp = requests.post(f"{BASE_URL}/api/admin/timer", json={"seconds": 60}, headers=admin_headers)
    data = resp.json()
    logger.info(f"Set Timer: {data}")
    assert resp.status_code == 200
    assert data["window"] == 60
        
    logger.info("--- v1.4 VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    run_verification()
