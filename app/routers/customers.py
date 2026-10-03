from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import json
import random

from .. import crud, schemas
from ..database import get_db
from ..services import ml_service 
from ..models import Customer, ScoreHistory, PreviousLoan

router = APIRouter(
    prefix="/customers", 
    tags=["Customers and Applications"],
)

@router.get("/", response_model=List[schemas.Customer])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return customers

@router.get("/status/{token}", response_model=schemas.Customer)
def get_customer_status(token: str, db: Session = Depends(get_db)):
    # Reverted to simple token lookup since unique=True is back
    db_customer = crud.get_customer_by_token(db, customer_token=token)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="No application found")
    
    # Fetch relations
    history = db.query(ScoreHistory).filter(ScoreHistory.customer_id == db_customer.id).all()
    prev_loans = db.query(PreviousLoan).filter(PreviousLoan.pan_ssn == db_customer.pan_ssn).all()
    
    setattr(db_customer, 'score_history', history)
    setattr(db_customer, 'previous_loans', prev_loans)
    return db_customer

@router.post("/", response_model=schemas.Customer, status_code=201)
def register_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """Registers a new loan application with advanced data points."""
    # RESTORED duplicate check (Revert)
    db_customer = crud.get_customer_by_token(db, customer_token=customer.customer_token)
    if db_customer:
        raise HTTPException(status_code=400, detail="Customer token already registered.")
    
    # --- 15L LIMIT CHECK ---
    existing_loans = db.query(Customer).filter(
        Customer.pan_ssn == customer.pan_ssn,
        Customer.review_status == "Approved"
    ).all()
    
    total_existing_amount = sum(l.loan_amount for l in existing_loans)
    
    if total_existing_amount + customer.loan_amount > 1500000:
        raise HTTPException(
            status_code=400, 
            detail=f"Loan Limit Exceeded. You have {total_existing_amount/100000}L in active loans. Limit is 15L."
        )

    dti = crud.calculate_dti(customer.loan_amount, customer.annual_income)
    
    new_customer = Customer(
        customer_token=customer.customer_token,
        loan_amount=customer.loan_amount,
        annual_income=customer.annual_income,
        credit_score=customer.credit_score,
        dti_ratio=dti,
        date_of_birth=customer.date_of_birth,
        years_employed=customer.years_employed,
        education_type=customer.education_type,
        pan_ssn=customer.pan_ssn,
        # New Fields
        phone_number=customer.phone_number,
        email_address=customer.email_address,
        residential_status=customer.residential_status,
        months_at_address=customer.months_at_address,
        phone_contract_type=customer.phone_contract_type,
        
        risk_level="Pending Score",
        model_version="N/A"
    )
    
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    # --- AUTO-GENERATE HISTORY (Dynamic) ---
    # Automatically generate 1-3 random previous loans for ANY new applicant
    num_loans = random.randint(1, 3)
    for _ in range(num_loans):
        amount = random.choice([50000, 100000, 200000, 300000, 500000])
        status = random.choice(["Paid", "Paid", "Active", "Defaulted"]) # Weighted towards Paid
        days_ago = random.randint(100, 1500)
        
        hist_loan = PreviousLoan(
            customer_id=new_customer.id,
            pan_ssn=new_customer.pan_ssn,
            amount=amount,
            status=status,
            disbursement_date=datetime.now() - timedelta(days=days_ago)
        )
        db.add(hist_loan)
    
    db.commit()
    # ---------------------------------------

    return new_customer

@router.get("/{customer_id}", response_model=schemas.Customer)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    history = db.query(ScoreHistory).filter(ScoreHistory.customer_id == customer_id).all()
    prev_loans = db.query(PreviousLoan).filter(PreviousLoan.pan_ssn == db_customer.pan_ssn).all()
    
    setattr(db_customer, 'score_history', history)
    setattr(db_customer, 'previous_loans', prev_loans)
    return db_customer

@router.post("/score/{customer_id}", response_model=schemas.CustomerScoreResponse)
def score_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    policy_rejection = False
    policy_reasons = []
    fraud_alert_msg = None
    
    # --- 1. FRAUD DETECTION RING (Security) ---
    # Check if phone/email is used by other customers
    dup_phone = db.query(Customer).filter(Customer.phone_number == db_customer.phone_number, Customer.id != db_customer.id).count()
    dup_email = db.query(Customer).filter(Customer.email_address == db_customer.email_address, Customer.id != db_customer.id).count()
    
    if dup_phone > 0 or dup_email > 0:
        fraud_alert_msg = f"🚨 FRAUD ALERT: Contact info linked to {dup_phone + dup_email} other applications."
        # We don't auto-reject, but we flag it heavily in the UI
    
    # --- 2. POLICY CHECK ---
    score_val = db_customer.credit_score if db_customer.credit_score is not None else 0
    if score_val < 400:
        policy_rejection = True
        policy_reasons.append(f"Credit Score ({score_val}) is below minimum threshold of 400.")

    # --- CIBIL OVERRIDE ---
    cibil_override = False
    if score_val < 650 and not policy_rejection:
        cibil_override = True

    if db_customer.annual_income > 0 and (db_customer.loan_amount / db_customer.annual_income) > 10:
        policy_rejection = True
        policy_reasons.append(f"Loan amount is {db_customer.loan_amount / db_customer.annual_income:.1f}x annual income (Limit: 10x).")

    # --- 3. AI PREDICTION ---
    # (Feature Engineering Logic same as before...)
    try:
        dob_date = datetime.strptime(db_customer.date_of_birth, "%Y-%m-%d")
        days_birth = (dob_date - datetime.now()).days
    except (ValueError, TypeError):
        days_birth = -12000

    years = db_customer.years_employed if db_customer.years_employed is not None else 0
    days_employed = int(years * 365) * -1
    
    norm_bureau_score = max(0.0, min(1.0, (score_val - 300) / (850 - 300)))
    amt_annuity = db_customer.loan_amount / 20 

    feature_input = {
        'AMT_INCOME_TOTAL': db_customer.annual_income,
        'AMT_CREDIT': db_customer.loan_amount,
        'AMT_ANNUITY': amt_annuity,
        'DAYS_BIRTH': days_birth,
        'DAYS_EMPLOYED': days_employed,
        'EXT_SOURCE_2': norm_bureau_score,
        'EXT_SOURCE_3': norm_bureau_score,
        'REGION_POPULATION_RELATIVE': 0.02, 
        'DAYS_ID_PUBLISH': -3000,
        'NAME_EDUCATION_TYPE_Higher education': 1.0 if db_customer.education_type == "Higher education" else 0.0,
        'NAME_EDUCATION_TYPE_Secondary / secondary special': 1.0 if db_customer.education_type == "Secondary" else 0.0,
        'NAME_EDUCATION_TYPE_Incomplete higher': 1.0 if db_customer.education_type == "Incomplete higher" else 0.0,
        'NAME_EDUCATION_TYPE_Lower secondary': 1.0 if db_customer.education_type == "Lower secondary" else 0.0,
        'NAME_EDUCATION_TYPE_Academic degree': 1.0 if db_customer.education_type == "Academic degree" else 0.0,
        'NAME_EDUCATION_TYPE_Civil service': 0.0, 
        'NAME_EDUCATION_TYPE_Others': 0.0, 
    }
    
    prediction_result = ml_service.predict_risk_and_explain(feature_input)

    # --- 4. PSYCHOMETRIC ADJUSTMENT (Innovation) ---
    # If borderline risk, use stability data to nudge score
    # Logic: Postpaid phone + Owned Home + >2 years at address = Reliable
    stability_score = 0
    if db_customer.residential_status == "Owned": stability_score += 1
    if db_customer.phone_contract_type == "Postpaid": stability_score += 1
    if db_customer.months_at_address and db_customer.months_at_address > 24: stability_score += 1
    
    # If highly stable (3/3), reduce perceived risk probability by 5%
    if stability_score == 3:
        prediction_result["risk_score"] = max(0, prediction_result["risk_score"] - 0.05)
        prediction_result["explanation"].insert(0, {
            "feature": "PSYCHOMETRIC_BOOST",
            "value": 3,
            "impact": -0.05,
            "direction": "Negative" # Reduces Risk
        })

    # --- CIBIL OVERRIDE APPLICATION ---
    if cibil_override:
        if prediction_result["risk_level"] == "Low":
            prediction_result["risk_level"] = "Medium"
            prediction_result["explanation"].insert(0, {
                "feature": "CIBIL_OVERRIDE",
                "value": score_val,
                "impact": 0.0,
                "direction": "Positive" # Increases Risk Perception
            })

    # --- 5. OVERRIDE WITH POLICY ---
    if policy_rejection:
        prediction_result["risk_score"] = 0.99
        prediction_result["risk_level"] = "Rejected" # Updated Status
        for reason in policy_reasons:
            prediction_result["explanation"].insert(0, {
                "feature": f"POLICY_VIOLATION: {reason}",
                "value": 0,
                "impact": 1.0,
                "direction": "Positive" 
            })
    
    # --- 6. DYNAMIC PRICING (Business Value) ---
    # Calculate APR based on final risk score
    base_rate = 5.5 # Prime rate
    risk_premium = prediction_result["risk_score"] * 20 # Max 20% extra
    final_apr = base_rate + risk_premium
    
    # Store in result for frontend
    prediction_result["approved_interest_rate"] = round(final_apr, 2)
    if fraud_alert_msg:
        prediction_result["fraud_alert"] = fraud_alert_msg

    # Save to DB
    db_customer.risk_score = prediction_result["risk_score"]
    db_customer.risk_level = prediction_result["risk_level"]
    db_customer.model_version = prediction_result["model_version"]
    db_customer.approved_interest_rate = final_apr
    
    # Only auto-approve if low risk and no fraud
    if prediction_result["risk_score"] < 0.2 and not fraud_alert_msg:
        db_customer.review_status = "Approved"
    elif policy_rejection:
        db_customer.review_status = "Rejected"
    else:
        db_customer.review_status = "Flagged for Review"

    db.add(db_customer)
    new_history = ScoreHistory(
        customer_id=db_customer.id,
        risk_score=prediction_result["risk_score"],
        risk_level=prediction_result["risk_level"],
        model_version=prediction_result["model_version"],
        explanation_json=json.dumps(prediction_result["explanation"]),
        input_features_json=json.dumps(feature_input),
        policy_outcome_json=json.dumps(policy_reasons)
    )
    db.add(new_history)
    db.commit()
    db.refresh(db_customer)

    # Re-fetch relations to ensure they are included in response
    history = db.query(ScoreHistory).filter(ScoreHistory.customer_id == customer_id).all()
    prev_loans = db.query(PreviousLoan).filter(PreviousLoan.pan_ssn == db_customer.pan_ssn).all()
    
    setattr(db_customer, 'score_history', history)
    setattr(db_customer, 'previous_loans', prev_loans)

    return {
        "customer": db_customer,
        "prediction_details": prediction_result
    }