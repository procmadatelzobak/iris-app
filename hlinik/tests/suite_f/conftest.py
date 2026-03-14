"""
Suite F: The Grand Simulation - Test Fixtures
==============================================
Provides server launch, 3-context browser setup, and screenshot utilities.
"""

import pytest
import os
import subprocess
import time
import threading
from pathlib import Path
from .sim_utils import BASE_URL, SCREENSHOT_DIR, TEST_PORT

class TestServer:
    """Manages the test server lifecycle."""
    
    def __init__(self, port: int):
        self.port = port
        self.process = None
        
    def start(self):
        """Start the server with a clean database."""
        # Remove old database for clean slate
        db_path = Path("data/iris.db")
        if db_path.exists():
            db_path.unlink()
        
        # Start server
        self.process = subprocess.Popen(
            ["./venv/bin/python", "run.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "PORT": str(self.port)}
        )
        
        # Wait for server to be ready
        import requests
        for i in range(30):
            try:
                resp = requests.get(f"http://localhost:{self.port}/", timeout=1)
                if resp.status_code == 200:
                    print(f"✓ Server ready on port {self.port}")
                    return
            except:
                pass
            time.sleep(0.5)
        
        # If we get here, server failed. Check output.
        stdout, stderr = self.process.communicate(timeout=1)
        stderr_decoded = stderr.decode() if stderr else "No stderr"
        stdout_decoded = stdout.decode() if stdout else "No stdout"
        raise Exception(f"Server failed to start on port {self.port}.\nSTDERR:\n{stderr_decoded}\nSTDOUT:\n{stdout_decoded}")
    
    def stop(self):
        """Stop the server."""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            print("✓ Server stopped")


@pytest.fixture(scope="session")
def test_server():
    """Session-scoped server fixture."""
    server = TestServer(TEST_PORT)
    server.start()
    yield server
    server.stop()


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the test server."""
    return BASE_URL


@pytest.fixture(scope="session")
def screenshot_dir():
    """Ensure screenshot directory exists."""
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    return SCREENSHOT_DIR


@pytest.fixture(scope="function")
def simulation_contexts(browser, screenshot_dir):
    """
    Creates 3 independent browser contexts for parallel simulation:
    - admin_context: For the Admin user
    - user_context: For the regular User
    - agent_context: For the Agent
    
    Each context has its own cookies and session.
    """
    # Create contexts
    admin_context = browser.new_context()
    user_context = browser.new_context()
    agent_context = browser.new_context()
    
    # Create pages
    admin_page = admin_context.new_page()
    user_page = user_context.new_page()
    agent_page = agent_context.new_page()
    
    yield {
        "admin": {"context": admin_context, "page": admin_page},
        "user": {"context": user_context, "page": user_page},
        "agent": {"context": agent_context, "page": agent_page},
    }
    
    # Cleanup
    admin_context.close()
    user_context.close()
    agent_context.close()
