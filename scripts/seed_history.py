import sys
from pathlib import Path
from datetime import datetime, timedelta

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.models import PreviousLoan, Customer

db = SessionLocal()

# Demo PANs
pans = {
    "FGHIJ9780B": [ # High CIBIL User
        {"amount": 500000, "status": "Paid", "date": "2023-01-15"},
        {"amount": 1000000, "status": "Active", "date": "2024-06-10"} # Active loan for 15L limit test
    ],
    "FGHIJ4674U": [ # Low CIBIL User
        {"amount": 200000, "status": "Defaulted", "date": "2022-05-20"},
        {"amount": 50000, "status": "Paid", "date": "2021-03-10"}
    ],
    "FMHIJ2180B": [ # User from screenshot
         {"amount": 300000, "status": "Paid", "date": "2023-08-01"}
    ]
}

print("Seeding Previous Loan History...")

for pan, loans in pans.items():
    # Find customer ID if exists
    customer = db.query(Customer).filter(Customer.pan_ssn == pan).first()
    
    if not customer:
        # Create a dummy customer placeholder for the history
        print(f"  Creating dummy customer for PAN {pan}...")
        customer = Customer(
            customer_token=f"dummy_{pan}",
            loan_amount=0,
            annual_income=0,
            pan_ssn=pan,
            credit_score=0,
            dti_ratio=0,
            risk_level="Historical",
            model_version="Legacy"
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
    
    customer_id = customer.id
    
    for loan in loans:
        # Check if exists
        exists = db.query(PreviousLoan).filter(
            PreviousLoan.pan_ssn == pan, 
            PreviousLoan.amount == loan["amount"],
            PreviousLoan.status == loan["status"]
        ).first()
        
        if not exists:
            new_loan = PreviousLoan(
                customer_id=customer_id,
                pan_ssn=pan,
                amount=loan["amount"],
                status=loan["status"],
                disbursement_date=datetime.strptime(loan["date"], "%Y-%m-%d")
            )
            db.add(new_loan)
            print(f"  Added loan for {pan}: {loan['amount']} ({loan['status']})")
        else:
            print(f"  Loan already exists for {pan}: {loan['amount']}")

db.commit()
print("Seeding Complete.")
db.close()
