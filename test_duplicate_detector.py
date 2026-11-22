from copy import deepcopy
from decimal import Decimal

from sqlalchemy import select, or_

from app.database import SessionLocal
from app.models import FinancialTransaction
from app.validation.duplicate_detector import find_potential_duplicate


def test_duplicate_detection():

    db = SessionLocal()

    try:
        # Find an existing transaction that has vendor information.
        existing = db.scalars(
            select(FinancialTransaction)
            .where(
                or_(
                    FinancialTransaction.vendor_id.is_not(None),
                    FinancialTransaction.vendor_name_raw.is_not(None)
                )
            )
            .limit(1)
        ).first()

        if existing is None:
            print("No suitable transaction found. Import sample data first.")
            return

        # Reconstruct the transaction data.
        transaction_data = {
            "project_id": existing.project_id,
            "vendor_id": existing.vendor_id,
            "category_id": existing.category_id,
            "amount": str(existing.amount),
            "transaction_date": existing.transaction_date,
            "transaction_type": existing.transaction_type,
            "description": existing.description,
            "vendor_name": existing.vendor_name_raw or ""
        }

        resolved_vendor_id = existing.vendor_id

        print("\nTEST 1: Exact matching transaction")

        result = find_potential_duplicate(
            db,
            transaction_data,
        )

        assert result is not None
        assert result.transaction_id == existing.transaction_id

        print("PASS: Existing transaction detected.")

        # Test 2: Different amount
        print("\nTEST 2: Different amount")

        different_amount = deepcopy(transaction_data)
        different_amount["amount"] = str(
            Decimal(transaction_data["amount"]) + Decimal("100.00")
        )

        result = find_potential_duplicate(
            db,
            different_amount,
        )

        assert result is None

        print("PASS: Different amount was not flagged.")

        # Test 3: Different transaction date
        print("\nTEST 3: Different transaction date")

        different_date = deepcopy(transaction_data)
        different_date["transaction_date"] = (
            existing.transaction_date.replace(
                day=1 if existing.transaction_date.day != 1 else 2
            )
        )

        result = find_potential_duplicate(
            db,
            different_date,
        )

        assert result is None

        print("PASS: Different date was not flagged.")

        # Test 4: Different vendor
        print("\nTEST 4: Different vendor")

        if resolved_vendor_id is not None:
            different_vendor = deepcopy(transaction_data)

            different_vendor["vendor_id"] = 999999

            result = find_potential_duplicate(
                db,
                different_vendor
            )

            assert result is None
        else:
            different_vendor = deepcopy(transaction_data)
            different_vendor["vendor_name"] = "__different_vendor__"

            result = find_potential_duplicate(
                db,
                different_vendor,
                None
            )

        assert result is None

        print("PASS: Different vendor was not flagged.")

        print("\nAll duplicate detector tests passed.")

    finally:
        db.close()


if __name__ == "__main__":
    test_duplicate_detection()