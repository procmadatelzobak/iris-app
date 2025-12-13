from sqlalchemy.orm import Session
from .database import User, UserRole, SessionLocal
from .dependencies import get_password_hash

def seed_data():
    db = SessionLocal()
    try:
        # 1. Root
        if not db.query(User).filter(User.username == "root").first():
            print("Seeding Root...")
            root = User(
                username="root",
                password_hash=get_password_hash("master_control_666"), # Hardcoded master pwd
                role=UserRole.ADMIN,
                status_level="high"
            )
            db.add(root)

        # 2. Admins (1-4)
        for i in range(1, 5):
            username = f"admin{i}"
            if not db.query(User).filter(User.username == username).first():
                print(f"Seeding {username}...")
                admin = User(
                    username=username,
                    password_hash=get_password_hash(f"secure_admin_{i}"),
                    role=UserRole.ADMIN,
                    status_level="high"
                )
                db.add(admin)

        # 3. Agents (1-8)
        for i in range(1, 9):
            username = f"agent{i}"
            if not db.query(User).filter(User.username == username).first():
                print(f"Seeding {username}...")
                agent = User(
                    username=username,
                    password_hash=get_password_hash(f"agent_pass_{i}"),
                    role=UserRole.AGENT,
                    status_level="mid"
                )
                db.add(agent)

        # 4. Users (1-8)
        for i in range(1, 9):
            username = f"user{i}"
            if not db.query(User).filter(User.username == username).first():
                print(f"Seeding {username}...")
                user = User(
                    username=username,
                    password_hash=get_password_hash(f"subject_pass_{i}"),
                    role=UserRole.USER,
                    status_level="low",
                    credits=100
                )
                db.add(user)

        db.commit()
        print("Seeding complete.")
    except Exception as e:
        print(f"Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()
