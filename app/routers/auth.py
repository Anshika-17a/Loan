from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import database, models, schemas, auth_utils

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.Token)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # 1. Check if username already exists
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 2. Hash the password
    hashed_password = auth_utils.get_password_hash(user.password)
    
    # 3. Create new user record
    # Ensure role defaults to 'applicant' if missing/invalid
    role = user.role if user.role in ['applicant', 'banker'] else 'applicant'
    
    new_user = models.User(
        username=user.username,
        password_hash=hashed_password,
        role=role
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        print(f"DB Error during registration: {e}") # Log to console
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    
    # 4. Auto-login: Generate Token immediately
    access_token = auth_utils.create_access_token(
        data={"sub": new_user.username, "role": new_user.role}
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": new_user.role, 
        "username": new_user.username
    }

@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(database.get_db)):
    # 1. Find user by username
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # 2. Verify Password
    if not auth_utils.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # 3. Generate Token
    access_token = auth_utils.create_access_token(
        data={"sub": db_user.username, "role": db_user.role}
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": db_user.role, 
        "username": db_user.username
    }