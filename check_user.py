from app.database import SessionLocal
from app import models

def check_user():
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.username == "anh").first()
        if user:
            print(f"User 'anh' found. Role: {user.role}, Hash: {user.password_hash}")
        else:
            print("User 'anh' NOT found.")
    except Exception as e:
        print(f"Error checking user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_user()
