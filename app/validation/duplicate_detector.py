from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FinancialTransaction


def find_potential_duplicate(
    db: Session,
    transaction_data: dict
):
    """
    Find an existing transaction with matching financial attributes.

    Returns the existing transaction if a potential duplicate is found.
    Otherwise, returns None.
    """

    project_id = int(transaction_data["project_id"])
    category_id = int(transaction_data["category_id"])

    amount = Decimal(
        str(transaction_data["amount"])
    )

    description = str(
        transaction_data["description"]
    ).strip().casefold()

    transaction_type = str(
        transaction_data["transaction_type"]
    ).strip().upper()

    transaction_date = transaction_data["transaction_date"]

    vendor_id = transaction_data.get("vendor_id")

    vendor_name = str(
        transaction_data.get("vendor_name", "")
    ).strip().casefold()

    query = select(FinancialTransaction).where(
        FinancialTransaction.project_id == project_id,
        FinancialTransaction.category_id == category_id,
        FinancialTransaction.amount == amount,
        FinancialTransaction.description == description,
        FinancialTransaction.transaction_date == transaction_date,
        FinancialTransaction.transaction_type == transaction_type
    )

    if vendor_id is not None:
        query = query.where(
            FinancialTransaction.vendor_id == int(vendor_id)
        )
    elif vendor_name:
        query = query.where(
            FinancialTransaction.vendor_id.is_(None),
            FinancialTransaction.vendor_name_raw.is_not(None)
        )

    existing_transaction = db.scalar(query)

    if vendor_id is None and vendor_name and existing_transaction:
        if existing_transaction.vendor_name_raw.strip().casefold() != vendor_name:
            return None

    return existing_transaction