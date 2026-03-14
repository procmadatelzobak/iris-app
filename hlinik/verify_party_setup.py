import requests

BASE_URL = "http://localhost:8000"

def set_party_mode():
    s = requests.Session()
    
    # 1. Login as Root (Admin)
    print("Logging in as root...")
    res = s.post(f"{BASE_URL}/auth/login", data={"username": "root", "password": "master_control_666"})
    if res.status_code != 200:
        print(f"Login Failed: {res.text}")
        return
    
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get User ID for user1
    print("Fetching users...")
    r_users = s.get(f"{BASE_URL}/api/admin/data/users", headers=headers)
    users = r_users.json()
    user1 = next((u for u in users if u["username"] == "user1"), None)
    
    if not user1:
        print("User1 not found!")
        return

    print(f"User1 ID: {user1['id']}, Current Status: {user1['status_level']}")
    
    # 3. Set Status to Party
    print("Setting status to PARTY...")
    payload = {"user_id": user1["id"], "status": "party"}
    r_set = s.post(f"{BASE_URL}/api/admin/economy/set_status", json=payload, headers=headers)
    
    if r_set.status_code == 200:
        print("Success! Status set to PARTY.")
        print(r_set.json())
    else:
        print(f"Failed to set status: {r_set.text}")

if __name__ == "__main__":
    set_party_mode()
