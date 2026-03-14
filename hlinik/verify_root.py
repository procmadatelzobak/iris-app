
import requests
import json
import logging

# Config
BASE_URL = "http://localhost:8000"
ADMIN_USER = "admin1"
ADMIN_PASS = "secure_admin_1"

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
    logger.info("--- STARTING v1.6 ROOT CONTROL VERIFICATION ---")

    # 1. Login
    admin_token = get_token(ADMIN_USER, ADMIN_PASS)
    if not admin_token:
        logger.error("Auth failed")
        return
        
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Test Get State
    resp = requests.get(f"{BASE_URL}/api/admin/root/state", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    logger.info(f"Root State: {data}")
    assert "tax_rate" in data
    assert "power_cap" in data
    
    initial_cap = data["power_cap"]
    
    # 3. Test Update Constants
    new_cap = initial_cap + 50
    payload = {"tax_rate": 0.25, "power_cap": new_cap}
    resp = requests.post(f"{BASE_URL}/api/admin/root/update_constants", json=payload, headers=headers)
    assert resp.status_code == 200
    
    # Verify Update
    resp = requests.get(f"{BASE_URL}/api/admin/root/state", headers=headers)
    data = resp.json()
    assert data["power_cap"] == new_cap
    assert data["tax_rate"] == 0.25
    logger.info("Root Update Verification: OK")
    
    logger.info("--- v1.6 VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    run_verification()
