
import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_auth_flow():
    session = requests.Session()
    
    print("1. Testing GET / (Login Page)...")
    try:
        resp = session.get(f"{BASE_URL}/")
        print(f"   Status: {resp.status_code}")
        if resp.status_code != 200:
            print("   FAIL: Expected 200")
            print(f"   BODY: {resp.text}")
            return
    except Exception as e:
        print(f"   FAIL: Connection refused. Server running? {e}")
        return

    print("\n2. Testing Login (admin1)...")
    try:
        data = {"username": "admin1", "password": "secure_admin_1"}
        resp = session.post(f"{BASE_URL}/auth/login", data=data)
        print(f"   Status: {resp.status_code}")
        if resp.status_code != 200:
             print(f"   FAIL: {resp.text}")
        else:
             token = resp.json().get("access_token")
             print(f"   Success. Token: {token[:10]}...")
             
             # Set cookie manually if session didn't (API returns it but let's ensure)
             session.cookies.set("access_token", token)
    except Exception as e:
        print(f"   FAIL: {e}")

    print("\n3. Testing Admin Dashboard access (via /auth/terminal)...")
    try:
        resp = session.get(f"{BASE_URL}/auth/terminal")
        print(f"   Status: {resp.status_code}")
        if resp.status_code != 200:
            print("   FAIL: Could not access dashboard")
    except Exception as e:
        print(f"   FAIL: {e}")

    print("\n4. Testing Logout...")
    try:
        resp = session.get(f"{BASE_URL}/auth/logout", allow_redirects=False)
        print(f"   Status: {resp.status_code}")
        print(f"   Location: {resp.headers.get('location')}")
        
        if resp.status_code == 302 and resp.headers.get('location') == "/":
            print("   PASS: Redirected to /")
        elif resp.status_code == 307:
             print("   WARN: Temporary Redirect (307).")
        elif resp.status_code == 500:
             print("   FAIL: Server Error 500")
        else:
             print(f"   FAIL: Unexpected status {resp.status_code}")
             
    except Exception as e:
        print(f"   FAIL: {e}")

if __name__ == "__main__":
    test_auth_flow()
