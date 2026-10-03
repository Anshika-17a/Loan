import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, engine
from app import models, auth_utils

def seed_user():
    # Ensure tables exist
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.username == "anh").first()
        if not user:
            print("Creating default user 'anh'...")
            hashed_password = auth_utils.get_password_hash("password")
            new_user = models.User(
                username="anh",
                password_hash=hashed_password,
                role="banker"
            )
            db.add(new_user)
            db.commit()
            print("Default user created successfully.")
        else:
            print("User 'anh' already exists.")
    except Exception as e:
        print(f"Error seeding user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_user()
