import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# The DATABASE_URL is read from the .env file
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables.")

# Create the SQLAlchemy engine
# Setting 'pool_pre_ping' helps manage dropped connections
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_pre_ping=True
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models
Base = declarative_base()

# Dependency to get a database session (used in FastAPI routes)
def get_db():
    """Yields a database session that is automatically closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()