from app.database import SessionLocal
from app.models import Customer, PreviousLoan

db = SessionLocal()

print("--- Customers ---")
customers = db.query(Customer).all()
for c in customers:
    print(f"ID: {c.id}, Token: {c.customer_token}, PAN: {c.pan_ssn}, Status: {c.review_status}")

print("\n--- Previous Loans ---")
loans = db.query(PreviousLoan).all()
for l in loans:
    print(f"ID: {l.id}, CustomerID: {l.customer_id}, PAN: {l.pan_ssn}, Amount: {l.amount}")

db.close()
