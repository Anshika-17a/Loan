import sys
from pathlib import Path
from datetime import datetime
import json

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.models import Customer, PreviousLoan, ScoreHistory

db = SessionLocal()

# Demo Scenarios
scenarios = [
    {
        "token": "demo_high_cibil",
        "pan": "FGHIJ9780B",
        "income": 1200000,
        "loan": 500000,
        "score": 896,
        "history": [
            {"amount": 500000, "status": "Paid", "date": "2023-01-15"},
            {"amount": 1000000, "status": "Active", "date": "2024-06-10"}
        ]
    },
    {
        "token": "demo_low_cibil",
        "pan": "FGHIJ4674U",
        "income": 800000,
        "loan": 200000,
        "score": 350,
        "history": [
            {"amount": 100000, "status": "Active", "date": "2023-05-20"},
            {"amount": 17000, "status": "Paid", "date": "2022-03-10"}
        ]
    },
    {
        "token": "demo_screenshot_user",
        "pan": "FMHIJ2180B",
        "income": 644047,
        "loan": 599998,
        "score": 621,
        "history": [
            {"amount": 300000, "status": "Paid", "date": "2023-08-01"}
        ]
    }
]

print("Seeding Demo Data...")

for s in scenarios:
    # 1. Check/Create Customer (Active Application)
    customer = db.query(Customer).filter(Customer.customer_token == s["token"]).first()
    if not customer:
        print(f"  Creating active application for {s['token']} ({s['pan']})...")
        customer = Customer(
            customer_token=s["token"],
            loan_amount=s["loan"],
            annual_income=s["income"],
            credit_score=s["score"],
            dti_ratio=0.3, # Approx
            pan_ssn=s["pan"],
            date_of_birth="1990-01-01",
            years_employed=5,
            education_type="Graduate",
            residential_status="Owned",
            phone_contract_type="Postpaid",
            risk_level="Pending Score",
            model_version="v1.0"
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
    else:
        print(f"  Application already exists for {s['token']}")

    # 2. Seed History
    for h in s["history"]:
        exists = db.query(PreviousLoan).filter(
            PreviousLoan.pan_ssn == s["pan"],
            PreviousLoan.amount == h["amount"],
            PreviousLoan.status == h["status"]
        ).first()
        
        if not exists:
            new_loan = PreviousLoan(
                customer_id=customer.id,
                pan_ssn=s["pan"],
                amount=h["amount"],
                status=h["status"],
                disbursement_date=datetime.strptime(h["date"], "%Y-%m-%d")
            )
            db.add(new_loan)
            print(f"    Added history: {h['amount']} ({h['status']})")

db.commit()
db.close()
print("Seeding Complete.")
