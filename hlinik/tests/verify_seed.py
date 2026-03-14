from app.database import SessionLocal, User

def verify_seeding():
    db = SessionLocal()
    count = db.query(User).count()
    print(f"Total Users: {count}")
    
    admins = db.query(User).filter(User.role == "admin").count()
    print(f"Admins: {admins}")
    
    agents = db.query(User).filter(User.role == "agent").count()
    print(f"Agents: {agents}")
    
    users = db.query(User).filter(User.role == "user").count()
    print(f"Users: {users}")
    
    db.close()

if __name__ == "__main__":
    verify_seeding()
