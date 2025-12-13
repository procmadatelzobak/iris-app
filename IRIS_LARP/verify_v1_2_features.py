import asyncio
import websockets
import httpx
import json

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/connect"

async def get_token(username, password):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BASE_URL}/auth/login", data={"username": username, "password": password})
        if res.status_code != 200:
            print(f"Login failed for {username}: {res.text}")
            return None
        return res.json()["access_token"]

async def admin_approve_task(token, task_id):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BASE_URL}/api/admin/tasks/approve", 
                                json={"task_id": task_id, "reward": 500},
                                headers={"Authorization": f"Bearer {token}"})
        return res.json()

async def admin_global_bonus(token, amt):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BASE_URL}/api/admin/economy/global_bonus", 
                                json={"user_id": 0, "amount": amt, "reason": "TEST"},
                                headers={"Authorization": f"Bearer {token}"})
        return res.json()

async def admin_reset_global(token):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BASE_URL}/api/admin/economy/reset", 
                                headers={"Authorization": f"Bearer {token}"})
        return res.json()

async def run_test():
    print("--- STARTING v1.2 VERIFICATION ---")
    
    # 1. Login
    user_token = await get_token("user1", "subject_pass_1")
    admin_token = await get_token("admin1", "secure_admin_1")
    
    if not user_token or not admin_token:
        print("Failed to get tokens.")
        return

    print("Tokens Acquired.")

    # 2. Connect Sockets
    async with websockets.connect(f"{WS_URL}?token={user_token}") as user_ws, \
               websockets.connect(f"{WS_URL}?token={admin_token}") as admin_ws:
        
        # Drain init messages
        # Admin gets init
        await admin_ws.recv() 
        # User gets user_status
        user_init = json.loads(await user_ws.recv())
        print(f"User Init 1: {user_init}")
        # Might receive task_update if task exists? 
        
        # --- TEST 1: TASK FLOW ---
        print("\n[TEST 1] Task Request Flow")
        await user_ws.send(json.dumps({"type": "task_request"}))
        print("User sent task_request.")
        
        # User should get Pending update
        while True:
            msg = json.loads(await user_ws.recv())
            if msg.get("type") == "task_update":
                print(f"User received Task Update: {msg}")
                if msg.get("status") == "pending_approval":
                     print("SUCCESS: User sees Pending Task.")
                     break
        
        # Admin should see broadcast? (Actually broadcast to admins only if implemented... yes admin_refresh_tasks)
        # But we need to drain admin socket or assume it arrived.
        # Let's verify via API that task exists.
        async with httpx.AsyncClient() as client:
             res = await client.get(f"{BASE_URL}/api/admin/tasks", headers={"Authorization": f"Bearer {admin_token}"})
             tasks = res.json()
             target_task = next((t for t in tasks if t["user_id"] == 14 and t["status"] == "pending_approval"), None)
             # User1 ID depends on seed. Usually 14 if seeded last.
             # Actually let's just find ANY pending task.
             target_task = next((t for t in tasks if t["status"] == "pending_approval" and t["prompt"] == "Waiting for assignment..."), None)
             
             if not target_task:
                 print("FAILED: Admin API did not see pending task.")
                 return
             print(f"Admin API sees Pending Task ID: {target_task['id']}")
             
             # Approve
             print("Admin approving task...")
             await admin_approve_task(admin_token, target_task["id"])
        
        # User should get Active update
        while True:
             msg = json.loads(await user_ws.recv())
             if msg.get("type") == "task_update" and msg.get("status") == "active":
                 print(f"SUCCESS: User received ACTIVE Task Update. Reward: {msg.get('reward')}")
                 break
                 
        # --- TEST 2: GLOBAL ECONOMY ---
        print("\n[TEST 2] Global Economy Injection")
        print("Admin injecting 333 credits...")
        await admin_global_bonus(admin_token, 333)
        
        while True:
            msg = json.loads(await user_ws.recv())
            if msg.get("type") == "economy_update":
                 print(f"User received Eco Update: {msg.get('credits')} (Msg: {msg.get('msg')})")
                 if "333" in str(msg.get("msg")) or msg.get("msg") == "GLOBAL STIMULUS: TEST": 
                      print("SUCCESS: Global Bonus received.")
                      break
        
        # --- TEST 3: ROOT RESET ---
        print("\n[TEST 3] Global Reset")
        print("Admin resetting economy...")
        await admin_reset_global(admin_token)
        
        while True:
            msg = json.loads(await user_ws.recv())
            if msg.get("type") == "user_status": # Reset sends user_status with 100
                 print(f"User received Status Reset: {msg}")
                 if msg.get("credits") == 100:
                      print("SUCCESS: Economy Reset Confirmed.")
                      break

    print("\n--- ALL TESTS PASSED ---")

if __name__ == "__main__":
    asyncio.run(run_test())
