from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional

# --- Helper Function: Calculate Debt-to-Income (DTI) ---
# NOTE: In a real system, we'd fetch actual monthly debt payments.
# For simplicity, we'll simulate a debt calculation for feature engineering.

def calculate_dti(loan_amount: float, annual_income: float) -> float:
    """
    Simulated automated feature engineering: Debt-to-Income Ratio (DTI).
    DTI = (Total Monthly Debt Payments) / (Gross Monthly Income)
    Let's assume a simplified monthly payment (M) = loan_amount / (12 * 5 years)
    and Gross Monthly Income (GMI) = annual_income / 12
    """
    # Assume 5-year loan term for monthly debt calculation
    MONTHS_IN_FIVE_YEARS = 60
    
    # Simplified Estimated Monthly Debt Payment based on the requested loan
    estimated_monthly_payment = loan_amount / MONTHS_IN_FIVE_YEARS
    
    # Gross Monthly Income
    gross_monthly_income = annual_income / 12
    
    # Avoid division by zero
    if gross_monthly_income <= 0:
        return 0.0

    dti = estimated_monthly_payment / gross_monthly_income
    
    # Cap DTI at a reasonable max value (e.g., 1.0 or 100%)
    return min(dti, 1.0)


# --- CRUD Operations ---

def get_customer(db: Session, customer_id: int) -> Optional[models.Customer]:
    """Retrieve a single customer by their internal ID."""
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()

def get_customer_by_token(db: Session, customer_token: str) -> Optional[models.Customer]:
    """Retrieve a single customer by their unique external token."""
    return db.query(models.Customer).filter(models.Customer.customer_token == customer_token).first()

def get_customers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Customer]:
    """Retrieve a list of customers."""
    return db.query(models.Customer).offset(skip).limit(limit).all()

def create_customer(db: Session, customer: schemas.CustomerCreate) -> models.Customer:
    """
    Creates a new customer record, performs server-side feature engineering,
    and saves the record to the database.
    """
    # 1. Automated Feature Engineering (SERVER SIDE)
    # This is a non-negotiable step for production-ready systems.
    dti = calculate_dti(customer.loan_amount, customer.annual_income)

    # 2. Create the ORM object
    db_customer = models.Customer(
        customer_token=customer.customer_token,
        loan_amount=customer.loan_amount,
        annual_income=customer.annual_income,
        credit_score=customer.credit_score,
        dti_ratio=dti,  # Store the computed feature
        risk_level="Pending Score", # Initial status
        model_version="N/A" # Initial status
    )
    
    # 3. Commit to DB
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer) # Get the DB-assigned ID and timestamps
    
    # IMPORTANT: The model scoring will happen in the *next* step.
    return db_customer