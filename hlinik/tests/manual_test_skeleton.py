import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine, init_db, SessionLocal
from app.main import app

def test_db_connection():
    try:
        init_db()
        print("Database initialized.")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connection test:", result.fetchone())
    except Exception as e:
        print(f"Database error: {e}")
        sys.exit(1)

def test_app_import():
    if app:
        print("FastAPI app imported successfully.")
    else:
        print("Failed to import app.")
        sys.exit(1)

if __name__ == "__main__":
    test_db_connection()
    test_app_import()
