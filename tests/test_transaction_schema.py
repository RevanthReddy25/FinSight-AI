from datetime import date
from decimal import Decimal

from pydantic import ValidationError

from app.schemas import FinancialTransactionCreate


# Valid transaction
valid_transaction = {
    "project_id": 1,
    "vendor_id": 2,
    "category_id": 1,
    "description": "Monthly AWS cloud expenses",
    "amount": "45000.00",
    "transaction_date": date.today(),
    "transaction_type": "EXPENSE",
    "status": "APPROVED"
}


try:

    transaction = FinancialTransactionCreate(
        **valid_transaction
    )

    print("Valid transaction accepted!")

    print("Amount:", transaction.amount)

    print("Amount type:", type(transaction.amount))

except ValidationError as error:

    print(error)


# Invalid transaction
invalid_transaction = {
    "project_id": 1,
    "vendor_id": 2,
    "category_id": 1,
    "description": "Invalid expense",
    "amount": "-5000.00",
    "transaction_date": date.today(),
    "transaction_type": "EXPENSE",
    "status": "APPROVED"
}


try:

    transaction = FinancialTransactionCreate(
        **invalid_transaction
    )

except ValidationError as error:

    print("\nInvalid transaction rejected!")

    print(error)