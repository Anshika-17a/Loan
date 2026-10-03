from app.database import SessionLocal
from app.models import Customer, PreviousLoan
from datetime import datetime, timedelta

db = SessionLocal()

pan = "ABCDE1234F"
customer = db.query(Customer).filter(Customer.pan_ssn == pan).first()

if customer:
    print(f"Found customer {pan}. Adding history...")
    
    # Check if history already exists
    exists = db.query(PreviousLoan).filter(PreviousLoan.pan_ssn == pan).first()
    if not exists:
        l1 = PreviousLoan(
            customer_id=customer.id,
            pan_ssn=pan,
            amount=200000,
            status="Paid",
            disbursement_date=datetime.now() - timedelta(days=400)
        )
        l2 = PreviousLoan(
            customer_id=customer.id,
            pan_ssn=pan,
            amount=50000,
            status="Active",
            disbursement_date=datetime.now() - timedelta(days=150)
        )
        db.add(l1)
        db.add(l2)
        db.commit()
        print("History added for vijay.")
    else:
        print("History already exists for vijay.")
else:
    print(f"Customer {pan} not found.")

db.close()
