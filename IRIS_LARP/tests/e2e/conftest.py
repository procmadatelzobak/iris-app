"""
Pytest fixtures for E2E testing with Playwright.
Starts a test server on port 8001 with clean database.
"""
import pytest
import threading
import time
import uvicorn
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestServer:
    """Manages test server lifecycle."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8001):
        self.host = host
        self.port = port
        self.thread = None
        self.server = None
        
    def start(self):
        """Start the uvicorn server in a background thread."""
        # Initialize fresh database before starting
        from app.database import init_db
        from app.seed import seed_data
        
        # Reset database
        init_db()
        seed_data()
        
        # Configure uvicorn
        config = uvicorn.Config(
            "app.main:app",
            host=self.host,
            port=self.port,
            log_level="warning",
            access_log=False
        )
        self.server = uvicorn.Server(config)
        
        # Run in thread
        self.thread = threading.Thread(target=self.server.run, daemon=True)
        self.thread.start()
        
        # Wait for server to be ready
        time.sleep(2)
        
    def stop(self):
        """Stop the server."""
        if self.server:
            self.server.should_exit = True
        if self.thread:
            self.thread.join(timeout=5)


@pytest.fixture(scope="session")
def test_server():
    """Fixture that provides a running test server."""
    # Change to project directory
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_dir)
    
    server = TestServer()
    server.start()
    
    yield f"http://{server.host}:{server.port}"
    
    server.stop()


@pytest.fixture(scope="session")
def base_url(test_server):
    """Returns the base URL for the test server."""
    return test_server


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for testing."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }
