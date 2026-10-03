from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# --- AUTH SCHEMAS ---
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "applicant" # 'banker' or 'applicant'

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

# --- AUDIT LOG ---
class ScoreHistoryBase(BaseModel):
    risk_score: float
    risk_level: str
    model_version: str
    explanation_json: str 
    input_features_json: str 
    policy_outcome_json: str 

class ScoreHistory(ScoreHistoryBase):
    id: int
    customer_id: int
    timestamp: datetime
    class Config:
        from_attributes = True

class PreviousLoan(BaseModel):
    id: int
    amount: float
    status: str
    disbursement_date: datetime
    pan_ssn: Optional[str] = None
    
    class Config:
        from_attributes = True

# --- CUSTOMER SCHEMAS ---
class CustomerCreate(BaseModel):
    customer_token: str = Field(..., max_length=50)
    loan_amount: float = Field(..., gt=0)
    annual_income: float = Field(..., gt=0)
    credit_score: int = Field(..., ge=0, le=850)
    date_of_birth: str = Field(..., description="YYYY-MM-DD")
    years_employed: float = Field(..., ge=0)
    education_type: str
    pan_ssn: str
    phone_number: str
    email_address: str
    residential_status: str
    months_at_address: int
    phone_contract_type: str

class Customer(BaseModel):
    id: int
    customer_token: str
    loan_amount: float
    annual_income: float
    credit_score: Optional[int] = None
    dti_ratio: Optional[float] = None
    date_of_birth: Optional[str] = None
    years_employed: Optional[float] = None
    education_type: Optional[str] = None
    pan_ssn: Optional[str] = None
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    residential_status: Optional[str] = None
    months_at_address: Optional[int] = None
    phone_contract_type: Optional[str] = None
    approved_interest_rate: Optional[float] = None
    review_status: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    model_version: str
    created_at: datetime
    updated_at: Optional[datetime] = None 
    score_history: List[ScoreHistory] = []
    previous_loans: List[PreviousLoan] = []

    class Config:
        from_attributes = True

class SHAPExplanation(BaseModel):
    feature: str
    value: float
    impact: float
    direction: str

class PredictionDetails(BaseModel):
    risk_score: float
    risk_level: str
    explanation: List[SHAPExplanation]
    model_version: str
    approved_interest_rate: Optional[float] = None
    fraud_alert: Optional[str] = None

class CustomerScoreResponse(BaseModel):
    customer: Customer
    prediction_details: PredictionDetails