from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
from . import models
from .database import engine, SessionLocal
from . import auth_utils
from .routers import customers
from .routers import plaid 
from .routers import auth

# --- CRITICAL: RESET DB ON STARTUP ---
# This drops old tables (fixing the missing column error) and creates fresh ones.
# models.Base.metadata.drop_all(bind=engine) 
models.Base.metadata.create_all(bind=engine)
# -------------------------------------

app = FastAPI(title="EWS Loan Risk Scoring API")

# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Incoming request: {request.method} {request.url}")
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Request completed: {response.status_code} in {process_time:.4f}s")
    return response

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https?://.*", # Allow all http/https origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup Event
@app.on_event("startup")
def startup_event():
    # Create tables if they don't exist
    models.Base.metadata.create_all(bind=engine)
    
    # Seed default user
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
            print("Default user created.")
    except Exception as e:
        print(f"Error seeding user: {e}")
    finally:
        db.close()

# Routers
app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(plaid.router)

@app.get("/")
def read_root():
    return {"message": "EWS API is running."}