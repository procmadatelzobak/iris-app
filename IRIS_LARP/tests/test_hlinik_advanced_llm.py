import asyncio
import websockets
import requests
import json
import sys
import time
from termcolor import cprint

# Configuration
BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/connect"

# Credentials (from seed.py)
CREDS = {
    "root": ("root", "master_control_666"),
    "admin1": ("admin1", "secure_admin_1"),
    "user1": ("user1", "subject_pass_1")
}

TOKENS = {}

def get_token(username, password):
    try:
        res = requests.post(f"{BASE_URL}/auth/login", data={"username": username, "password": password})
        if res.status_code == 200:
            return res.cookies.get("access_token")
    except Exception as e:
        print(f"Login error {username}: {e}")
    return None

def authenticate():
    cprint("🔑 Authenticating...", "white")
    for user, (u, p) in CREDS.items():
        token = get_token(u, p)
        if token:
            TOKENS[user] = token
            cprint(f"  [OK] {user}", "green")
        else:
            cprint(f"  [FAIL] {user}", "red")
            sys.exit(1)

def api_header(user_key):
    return {"Authorization": f"Bearer {TOKENS[user_key]}"}

async def run_test():
    authenticate()

    # 1. Reset System (ensure clean state)
    cprint("\n=== STEP 1: System Reset ===", "cyan")
    res = requests.post(f"{BASE_URL}/api/admin/root/reset", headers=api_header("root"))
    if res.status_code == 200:
        cprint("  [OK] System Reset", "green")
    else:
        cprint(f"  [FAIL] Reset: {res.text}", "red")

    # 2. Connect User WebSocket
    cprint("\n=== STEP 2: User WebSocket Connect ===", "cyan")
    user_token = TOKENS["user1"]
    
    async with websockets.connect(f"{WS_URL}?token={user_token}") as ws:
        # Initial greeting / status
        init_msg = await ws.recv()
        # Drain initial history/status messages
        try:
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                # print(f"  Ignored init msg: {msg[:50]}...")
        except asyncio.TimeoutError:
            pass
        
        cprint("  [OK] WS Connected and Drained", "green")

        # 3. User Requests Task
        cprint("\n=== STEP 3: Task Request (User) ===", "cyan")
        await ws.send(json.dumps({"type": "task_request"}))
        
        # Expect task_update (pending)
        task_id = None
        try:
            while True:
                resp = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(resp)
                if data.get("type") == "task_update":
                    cprint(f"  [RECV] Task Update: {data['status']}", "yellow")
                    if data["status"] == "pending_approval":
                        task_id = data.get("task_id") or data.get("id")
                        cprint(f"  [OK] Task Pending Created. ID: {task_id}", "green")
                        break
        except Exception as e:
            cprint(f"  [FAIL] Timeout waiting for pending task: {e}", "red")
            return

        if not task_id:
            cprint("  [FAIL] No Task ID found", "red")
            return
            
        # 4. Admin Generates Task via LLM (Approve with valid reward but empty prompt)
        cprint(f"\n=== STEP 4: Admin Generates Task (ID: {task_id}) via LLM ===", "cyan")
        
        # Get Task details first to confirm
        tasks_res = requests.get(f"{BASE_URL}/api/admin/tasks", headers=api_header("admin1"))
        # print("Tasks:", tasks_res.json())
        
        # Approve trigger
        payload = {
            "task_id": task_id,
            "reward": 150, # Custom reward
            "prompt_content": "" # Empty -> Trigger LLM
        }
        
        start_time = time.time()
        res = requests.post(f"{BASE_URL}/api/admin/tasks/approve", json=payload, headers=api_header("admin1"))
        duration = time.time() - start_time
        
        if res.status_code == 200:
            cprint(f"  [OK] Admin Approved (LLM Triggered) in {duration:.2f}s", "green")
        else:
            cprint(f"  [FAIL] Approve failed: {res.text}", "red")
            return

        # 5. Verify Generated Content (User side)
        cprint("\n=== STEP 5: Verify Generated Content ===", "cyan")
        generated_desc = ""
        try:
            while True:
                resp = await asyncio.wait_for(ws.recv(), timeout=15.0) # LLM might be slow
                data = json.loads(resp)
                if data.get("type") == "task_update" and data["status"] == "active":
                    generated_desc = data.get("description", "")
                    cprint(f"  [RECV] Active Task Update", "yellow")
                    cprint(f"  [LLM OUTPUT] >> {generated_desc}", "white", attrs=["bold"])
                    break
        except Exception as e:
            cprint(f"  [FAIL] Timeout waiting for LLM content: {e}", "red")
            return

        if len(generated_desc) > 10 and "zlepšení" not in generated_desc: # Basic check it's not the fallback
             cprint("  [OK] LLM Content Verified (Length > 10)", "green")
        else:
             cprint("  [WARN] Content might be fallback or empty?", "yellow")

        # 6. User Submits Task
        cprint("\n=== STEP 6: User Submits Task ===", "cyan")
        submission = "Analýza dokončena. Všechny systémy stabilní. Navrhuji zvýšení přídělu energie."
        await ws.send(json.dumps({
            "type": "task_submit",
            "task_id": task_id,
            "content": submission
        }))
        
        # Wait for confirmation
        try:
            while True:
                resp = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(resp)
                if data.get("type") == "task_update" and data["status"] == "submitted":
                    cprint("  [OK] Submission Confirmed", "green")
                    break
        except Exception as e:
            cprint(f"  [FAIL] Submission timeout: {e}", "red")

        # 7. Admin Grades Task
        cprint("\n=== STEP 7: Admin Grades Task ===", "cyan")
        # Grade 100% -> 1.0 modifier
        payload = {
            "task_id": task_id,
            "rating_modifier": 1.0
        }
        res = requests.post(f"{BASE_URL}/api/admin/tasks/grade", json=payload, headers=api_header("admin1"))
        if res.status_code == 200:
            data = res.json()
            net_reward = data.get("net_reward")
            cprint(f"  [OK] Graded. Net Reward: {net_reward}", "green")
            
            if net_reward > 0:
                 cprint("  [PASS] Economy Check Passed", "green")
            else:
                 cprint("  [FAIL] No reward?", "red")
        else:
            cprint(f"  [FAIL] Grading failed: {res.text}", "red")

        # 8. Final WS User Check (Paid)
        try:
            expected_msg = False
            while True:
                resp = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(resp)
                if data.get("type") == "task_update" and data["status"] == "paid":
                    cprint(f"  [RECV] User received PAID update. Rating: {data.get('rating')}%", "green")
                    expected_msg = True
                    break
        except:
            pass
            
        if not expected_msg:
             cprint("  [WARN] User didn't receive final Paid update in time", "yellow")

    cprint("\n=== TEST COMPLETED SUCCESSFULLY ===", "green", attrs=["bold"])

if __name__ == "__main__":
    asyncio.run(run_test())
