from datetime import date

from app.database import SessionLocal
from app.models import FinancialTransaction


db = SessionLocal()

try:
    transaction = FinancialTransaction(
        project_id=1,
        category_id=1,
        description="ACID rollback test",
        amount=1000,
        transaction_date=date.today(),
        transaction_type="EXPENSE",
        status="PENDING"
    )

    db.add(transaction)
    db.flush()

    print("Transaction flushed successfully.")

    transaction_id = transaction.transaction_id

    print("Generated transaction ID:", transaction_id)

    db.rollback()

    print("Transaction rolled back.")

    saved_transaction = db.get(
        FinancialTransaction,
        transaction_id
    )

    print("Transaction after rollback:", saved_transaction)

finally:
    db.close()