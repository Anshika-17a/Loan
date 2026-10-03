from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# --- USER TABLE (For Auth) ---
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="applicant")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- CUSTOMER TABLE ---
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    # RESTORED unique=True (Revert)
    customer_token = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)

    # Financial Features
    loan_amount = Column(Float, nullable=False)
    annual_income = Column(Float, nullable=False)
    credit_score = Column(Integer)
    dti_ratio = Column(Float)
    
    # Real-World Fields
    date_of_birth = Column(String, nullable=True) 
    years_employed = Column(Float, nullable=True)
    education_type = Column(String, nullable=True)
    pan_ssn = Column(String, nullable=True)
    phone_number = Column(String, index=True, nullable=True)
    email_address = Column(String, index=True, nullable=True)
    residential_status = Column(String, nullable=True)
    months_at_address = Column(Integer, nullable=True)
    phone_contract_type = Column(String, nullable=True)
    
    # Risk/Audit Data
    risk_score = Column(Float, nullable=True) 
    risk_level = Column(String, nullable=True) 
    approved_interest_rate = Column(Float, nullable=True)
    review_status = Column(String, default="Auto-Decisioned")

    model_version = Column(String, default="v0.0.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_default_flag = Column(Boolean, nullable=True)

    # Relationship to ScoreHistory
    score_history = relationship("ScoreHistory", back_populates="customer")
    # Relationship to PreviousLoan
    previous_loans = relationship("PreviousLoan", back_populates="customer")

# --- HISTORY TABLE ---
class ScoreHistory(Base):
    __tablename__ = "score_history"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    model_version = Column(String, nullable=False)
    explanation_json = Column(String) 
    input_features_json = Column(String) 
    policy_outcome_json = Column(String) 

    customer = relationship("Customer", back_populates="score_history")

# --- PREVIOUS LOAN TABLE ---
class PreviousLoan(Base):
    __tablename__ = "previous_loans"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False) # e.g., "Paid", "Active", "Defaulted"
    disbursement_date = Column(DateTime(timezone=True), server_default=func.now())
    pan_ssn = Column(String, index=True, nullable=True)

    customer = relationship("Customer", back_populates="previous_loans")