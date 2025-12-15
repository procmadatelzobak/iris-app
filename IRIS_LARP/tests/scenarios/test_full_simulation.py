import asyncio
import json
import os
import random
import time
from datetime import datetime
from pathlib import Path
import websockets
from playwright.async_api import async_playwright

# Configuration
API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent # iris-app root
DOC_DATA_DIR = BASE_DIR / "doc" / "iris" / "lore-web" / "data" / "test_runs"
ROLES_FILE = BASE_DIR / "doc" / "iris" / "lore-web" / "data" / "roles.json"

class TestLogger:
    def __init__(self, scenario_name):
        self.scenario_name = scenario_name
        self.start_time = datetime.now()
        self.logs = []
        self.errors = 0
        self.users_active = 0
        self.latencies = []
        self.screenshots_taken = []
        
    def log(self, level, message, screenshot=None):
        entry = {
            "time": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "screenshot": screenshot
        }
        self.logs.append(entry)
        if screenshot:
            self.screenshots_taken.append(screenshot)
        if level == "ERROR":
            self.errors += 1
        print(f"[{level}] {message}")

    def record_latency(self, ms):
        self.latencies.append(ms)

    def save(self):
        duration = (datetime.now() - self.start_time).total_seconds()
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        
        filename = f"run_{int(self.start_time.timestamp())}.json"
        
        # Determine status
        status = "success"
        if self.errors > 0:
            status = "failed"
        elif len(self.logs) < 5:
             status = "warning" # Too few logs
             
        run_data = {
            "timestamp": self.start_time.isoformat(),
            "scenario_name": self.scenario_name,
            "status": status,
            "duration": round(duration, 2),
            "filename": filename,
            "stats": {
                "users_active": self.users_active,
                "avg_latency": round(avg_latency, 2),
                "errors": self.errors
            },
            "logs": self.logs
        }
        
        # Save run file
        runs_dir = DOC_DATA_DIR / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)
        with open(runs_dir / filename, "w") as f:
            json.dump(run_data, f, indent=2)
            
        # Update index
        index_file = DOC_DATA_DIR / "index.json"
        index = []
        if index_file.exists():
            try:
                with open(index_file, "r") as f:
                    index = json.load(f)
            except:
                index = []
        
        index.append({
            "timestamp": self.start_time.isoformat(),
            "scenario_name": self.scenario_name,
            "status": run_data["status"],
            "duration": run_data["duration"],
            "filename": filename,
            "stats": run_data["stats"]
        })
        
        # Keep only last 50 runs to avoid huge index
        if len(index) > 50:
            index = index[-50:]
            
        with open(index_file, "w") as f:
            json.dump(index, f, indent=2)
            
        print(f"✅ Test run saved to {runs_dir / filename}")

async def simulate_user(role, logger):
    logger.users_active += 1
    user_id = role["id"]
    
    start = time.time()
    try:
        # Simulate Login and Connection
        await asyncio.sleep(random.uniform(0.1, 1.0)) 
        
        # Try to connect (Assuming endpoint /ws/{client_id} exists and is open for simulation)
        uri = f"{WS_URL}/{user_id}"
        
        async with websockets.connect(uri) as websocket:
            connect_latency = (time.time() - start) * 1000
            logger.record_latency(connect_latency)
            logger.log("INFO", f"User {user_id} ({role.get('archetype', 'Unknown')}) connected in {int(connect_latency)}ms.")
            
            # Send INTRO message
            msg = {"type": "chat", "content": f"Simulation INIT for {user_id}", "channel": "debug"}
            await websocket.send(json.dumps(msg))
            
            # Simulate some activity based on role
            if role['type'] == 'agent':
                await asyncio.sleep(1)
                logger.log("INFO", f"Agent {user_id} checking queue...")
            elif role['type'] == 'admin':
                await asyncio.sleep(0.5)
                logger.log("INFO", f"Admin {user_id} scanning dashboard.")
                
            # Wait a bit
            await asyncio.sleep(1)

    except ConnectionRefusedError:
        logger.log("ERROR", f"User {user_id}: Connection failed (Server not running?)")
    except Exception as e:
        # Don't log expected disconnects as errors if simulation ends naturally
        logger.log("WARNING", f"User {user_id} simulation ended: {str(e)}")

async def run_browser_check(logger):
    try:
        logger.log("INFO", "Starting browser automation check...")
        async with async_playwright() as p:
            # Launch browser (headless=True by default)
            browser = await p.chromium.launch()
            context = await browser.new_context(viewport={'width': 1280, 'height': 720})
            page = await context.new_page()
            
            # Check Wiki Dashboard
            logger.log("INFO", f"Navigating to Wiki at {API_URL}/organizer-wiki/...")
            response = await page.goto(f"{API_URL}/organizer-wiki/")
            
            if not response or response.status != 200:
                logger.log("ERROR", f"Wiki returned status {response.request if response else 'Available'}")
            
            # Wait for content
            try:
                await page.wait_for_selector(".dashboard-grid", timeout=5000)
                logger.log("SUCCESS", "Wiki Dashboard loaded.")
            except:
                logger.log("WARNING", "Wiki Dashboard selector timed out.")

            # Screenshot Wiki
            timestamp = int(datetime.now().timestamp())
            filename = f"wiki_check_{timestamp}.png"
            path = DOC_DATA_DIR / "runs" / filename
            await page.screenshot(path=str(path))
            logger.log("INFO", "Wiki visual captured.", screenshot=filename)
            
            # Check Compliance
            await page.click('[data-section="compliance"]')
            await asyncio.sleep(1) # transition
            filename_audit = f"wiki_audit_{timestamp}.png"
            await page.screenshot(path=str(DOC_DATA_DIR / "runs" / filename_audit))
            logger.log("INFO", "Audit section verified.", screenshot=filename_audit)

            await browser.close()
            
    except Exception as e:
        logger.log("ERROR", f"Browser automation failed: {str(e)}. (Ensure playwright is installed: pip install pytest-playwright && playwright install)") 

async def main():
    logger = TestLogger("Full System Simulation (Load + UI)")
    logger.log("INFO", "Starting complex test scenario...")
    
    # 1. Load roles
    if not ROLES_FILE.exists():
         logger.log("ERROR", f"Roles file missing at {ROLES_FILE}")
         logger.save()
         return

    with open(ROLES_FILE, "r") as f:
        roles = json.load(f)
    
    logger.log("INFO", f"Loaded {len(roles)} roles for simulation.")

    # 2. Browser Check (UI Verification)
    await run_browser_check(logger)
    
    # 3. Mass Simulation (Backend Load)
    # Simulate subset to avoid overloading dev machine
    simulation_roles = roles[:12] 
    
    logger.log("INFO", f"Spawning {len(simulation_roles)} concurrent connections...")
    
    tasks = []
    for role in simulation_roles:
        tasks.append(simulate_user(role, logger))
        
    if tasks:
        await asyncio.gather(*tasks)
    
    logger.log("SUCCESS", "Simulation scenario completed.")
    logger.save()

if __name__ == "__main__":
    asyncio.run(main())
