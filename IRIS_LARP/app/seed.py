from sqlalchemy.orm import Session
from .database import User, UserRole, SessionLocal
from .dependencies import get_password_hash
import json
import os

def load_scenario():
    """Load default scenario from JSON file."""
    scenario_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'default_scenario.json')
    if os.path.exists(scenario_path):
        with open(scenario_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    # Fallback to hardcoded defaults
    return None

def seed_data():
    db = SessionLocal()
    scenario = load_scenario()
    
    try:
        # 1. Root
        root_cfg = scenario['users']['root'] if scenario else {
            "username": "root",
            "password": "master_control_666",
            "status_level": "high"
        }
        if not db.query(User).filter(User.username == root_cfg['username']).first():
            print(f"Seeding {root_cfg['username']}...")
            root = User(
                username=root_cfg['username'],
                password_hash=get_password_hash(root_cfg['password']),
                role=UserRole.ADMIN,
                status_level=root_cfg.get('status_level', 'high')
            )
            db.add(root)

        # 2. Admins
        admin_cfg = scenario['users']['admins'] if scenario else {
            "count": 4,
            "username_pattern": "admin{i}",
            "password_pattern": "secure_admin_{i}",
            "status_level": "high"
        }
        for i in range(1, admin_cfg['count'] + 1):
            username = admin_cfg['username_pattern'].format(i=i)
            password = admin_cfg['password_pattern'].format(i=i)
            if not db.query(User).filter(User.username == username).first():
                print(f"Seeding {username}...")
                admin = User(
                    username=username,
                    password_hash=get_password_hash(password),
                    role=UserRole.ADMIN,
                    status_level=admin_cfg.get('status_level', 'high')
                )
                db.add(admin)

        # 3. Agents
        agent_cfg = scenario['users']['agents'] if scenario else {
            "count": 8,
            "username_pattern": "agent{i}",
            "password_pattern": "agent_pass_{i}",
            "status_level": "mid"
        }
        for i in range(1, agent_cfg['count'] + 1):
            username = agent_cfg['username_pattern'].format(i=i)
            password = agent_cfg['password_pattern'].format(i=i)
            if not db.query(User).filter(User.username == username).first():
                print(f"Seeding {username}...")
                agent = User(
                    username=username,
                    password_hash=get_password_hash(password),
                    role=UserRole.AGENT,
                    status_level=agent_cfg.get('status_level', 'mid')
                )
                db.add(agent)

        # 4. Users
        user_cfg = scenario['users']['users'] if scenario else {
            "count": 8,
            "username_pattern": "user{i}",
            "password_pattern": "subject_pass_{i}",
            "status_level": "low",
            "initial_credits": 100
        }
        for i in range(1, user_cfg['count'] + 1):
            username = user_cfg['username_pattern'].format(i=i)
            password = user_cfg['password_pattern'].format(i=i)
            if not db.query(User).filter(User.username == username).first():
                print(f"Seeding {username}...")
                user = User(
                    username=username,
                    password_hash=get_password_hash(password),
                    role=UserRole.USER,
                    status_level=user_cfg.get('status_level', 'low'),
                    credits=user_cfg.get('initial_credits', 100)
                )
                db.add(user)

        db.commit()
        print("Seeding complete.")
    except Exception as e:
        print(f"Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()
