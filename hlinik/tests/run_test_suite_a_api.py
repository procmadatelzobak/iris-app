import requests
import sys
import json
from termcolor import cprint

BASE_URL = "http://127.0.0.1:8000"

# User Credentials from seed.py
CREDS = {
    "root": ("root", "master_control_666"),
    "admin1": ("admin1", "secure_admin_1"),
    "user1": ("user1", "subject_pass_1"), # "Agatha"
    "agent1": ("agent1", "agent_pass_1")   # "Krtek"
}

TOKENS = {}

def get_token(username, password):
    try:
        # Auth usually expects form-data for OAuth2 or simple JSON?
        # Iris auth uses form data typically for /auth/login often, but let's check.
        # Javascript used FormData.
        res = requests.post(f"{BASE_URL}/auth/login", data={"username": username, "password": password})
        if res.status_code == 200:
            # Check cookies
            return res.cookies.get("access_token")
        else:
            print(f"Login failed for {username}: {res.status_code} {res.text}")
    except Exception as e:
        print(f"Login exception for {username}: {e}")
    return None

def login_all():
    cprint("🔑 Authenticating test users...", "white", attrs=["bold"])
    for user, (u, p) in CREDS.items():
        token = get_token(u, p)
        if token:
            TOKENS[user] = token
            cprint(f"  [OK] {user.upper()}", "green")
        else:
            cprint(f"  [FAIL] {user.upper()}", "red")

def header(user):
    token = TOKENS.get(user)
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}

def block0_setup():
    cprint("\n=== BLOCK 0: SETUP (ROOT) ===", "cyan", attrs=["bold"])
    if "root" not in TOKENS:
        cprint("Skipping (ROOT not logged in)", "yellow")
        return

    # Verify Test Mode
    try:
        res = requests.get(f"{BASE_URL}/api/admin/root/ai_config", headers=header("root"))
        if res.status_code == 200:
            data = res.json()
            status = data.get("test_mode", False)
            cprint(f"  Test Mode Status: {status}", "green" if status else "yellow")
        else:
             cprint(f"  Failed to fetch config: {res.status_code}", "red")
    except Exception as e:
        cprint(f"  Connection Error: {e}", "red")

def block1_init():
    cprint("\n=== BLOCK 1: INITIALIZATION (ADMIN) ===", "cyan", attrs=["bold"])
    if "admin1" not in TOKENS:
        cprint("Skipping (ADMIN1 not logged in)", "yellow")
        return

    # 1. Reset
    cprint("  Resetting System...", "white")
    # Assuming ROOT is needed for reset, but let's see rights.
    # admin_api.py: @router.post("/root/reset") -> get_current_admin
    # Any admin can reset.
    requests.post(f"{BASE_URL}/api/admin/root/reset", headers=header("admin1"))
    
    # 2. Config Optimizer
    cprint("  Configuring Optimizer...", "white")
    # admin_api: @router.post("/optimizer/toggle")
    requests.post(f"{BASE_URL}/api/admin/optimizer/toggle", json={"active": True}, headers=header("admin1"))
    
    # 3. Verify
    try:
        res = requests.get(f"{BASE_URL}/api/admin/controls/state", headers=header("admin1"))
        state = res.json()
        cprint(f"  Optimizer: {state.get('optimizer_active')}", "green" if state.get('optimizer_active') else "red")
        
        res_root = requests.get(f"{BASE_URL}/api/admin/root/state", headers=header("admin1"))
        root_state = res_root.json()
        treasury = root_state.get('treasury', 0)
        cprint(f"  Treasury: {treasury}", "green" if treasury > 0 else "red")
    except Exception as e:
         cprint(f"  Error: {e}", "red")

def block2_request():
    cprint("\n=== BLOCK 2: THE REQUEST (USER1/AGATHA) ===", "cyan", attrs=["bold"])
    if "admin1" not in TOKENS: 
        cprint("Skipping verification (Admin needed to check User data)", "yellow")
        return

    try:
        res = requests.get(f"{BASE_URL}/api/admin/data/users", headers=header("admin1"))
        users = res.json()
        user1 = next((u for u in users if u['username'] == 'user1'), None)
        if user1:
            cprint(f"  User1 Credits: {user1['credits']}", "green" if user1['credits'] == 100 else "red")
        else:
            cprint("  User1 not found!", "red")
            
        cprint("  (Skipping WebSocket Task Request action)", "yellow")
    except Exception as e:
         cprint(f"  Error: {e}", "red")

def run_suite():
    login_all()
    if not TOKENS:
        cprint("No users authenticated. Aborting.", "red")
        sys.exit(1)
        
    block0_setup()
    block1_init()
    block2_request()
    
if __name__ == "__main__":
    run_suite()
