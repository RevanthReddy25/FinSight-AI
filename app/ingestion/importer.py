from decimal import Decimal
from datetime import date, datetime

import pandas as pd

from sqlalchemy.orm import Session

from app.models import FinancialTransaction

from app.vendor_resolution import (
    resolve_vendor,
    reconcile_unresolved_vendors
)

from app.validation.duplicate_detector import (
    find_potential_duplicate
)


def clean_value(value):
    """Convert missing Pandas values into empty strings."""

    if value is None or pd.isna(value):
        return ""

    return str(value).strip()


def import_financial_transactions(valid_df, db, batch_id=None):
    """
    Import validated financial transactions.

    Features:
    - Vendor resolution
    - Potential duplicate detection
    - Transaction insertion
    - Unresolved vendor reconciliation

    Potential duplicates are flagged, not automatically rejected.

    The caller is responsible for committing the database transaction.
    """

    imported_count = 0
    resolved_count = 0
    unresolved_count = 0
    potential_duplicate_count = 0

    potential_duplicates = []

    try:

        for _, row in valid_df.iterrows():

            # ----------------------------------
            # 1. Read and normalize vendor data
            # ----------------------------------

            vendor_id_value = clean_value(
                row.get("vendor_id", "")
            )

            vendor_name = clean_value(
                row.get("vendor_name", "")
            )

            vendor_id_input = (
                int(vendor_id_value)
                if vendor_id_value
                else None
            )

            # ----------------------------------
            # 2. Resolve vendor
            # ----------------------------------

            resolved_vendor_id = resolve_vendor(
                db=db,
                vendor_id=vendor_id_input,
                vendor_name=vendor_name
            )

            if resolved_vendor_id is not None:
                resolved_count += 1

            elif vendor_name:
                unresolved_count += 1

            # ----------------------------------
            # 3. Prepare normalized transaction data
            # ----------------------------------

            transaction_date_value = row["transaction_date"]

            if isinstance(transaction_date_value, datetime):
                transaction_date = transaction_date_value.date()

            elif isinstance(transaction_date_value, date):
                transaction_date = transaction_date_value

            else:
                transaction_date = date.fromisoformat(
                    str(transaction_date_value).strip()
                )

            transaction_data = row.to_dict()

            transaction_data.update({
                "vendor_id": resolved_vendor_id,
                "vendor_name": vendor_name,
                "amount": str(row["amount"]).strip(),
                "transaction_date": transaction_date,
                "description": clean_value(row["description"]),
                "transaction_type": clean_value(
                    row["transaction_type"]
                ).upper()
            })

            # ----------------------------------
            # 4. Detect potential duplicates
            # ----------------------------------

            existing_transaction = find_potential_duplicate(
                db,
                transaction_data
            )

            if existing_transaction:

                potential_duplicate_count += 1

                potential_duplicates.append({
                    "existing_transaction_id":
                        existing_transaction.transaction_id,

                    "description":
                        transaction_data["description"],

                    "amount":
                        str(transaction_data["amount"]),

                    "transaction_date":
                        str(transaction_date),

                    "vendor_name":
                        vendor_name,

                    "existing_batch_id":
                        existing_transaction.import_batch_id
                })

            # ----------------------------------
            # 5. Create transaction
            # ----------------------------------

            transaction = FinancialTransaction(

                project_id=int(row["project_id"]),

                vendor_id=resolved_vendor_id,

                vendor_name_raw=vendor_name or None,

                category_id=int(row["category_id"]),

                import_batch_id=batch_id,

                description=transaction_data["description"],

                amount=Decimal(transaction_data["amount"]),

                transaction_date=transaction_date,

                transaction_type=transaction_data["transaction_type"],

                status=clean_value(row["status"]).upper()
            )

            db.add(transaction)

            db.flush()

            imported_count += 1

        # ----------------------------------
        # 6. Reconcile older unresolved vendors
        # ----------------------------------

        reconciliation_result = (
            reconcile_unresolved_vendors(db)
        )

        # ----------------------------------
        # 7. Flush changes
        # ----------------------------------

        db.flush()

        # ----------------------------------
        # 8. Return import statistics
        # ----------------------------------

        return {
            "imported_transactions": imported_count,

            "resolved_vendors": resolved_count,

            "unresolved_transactions": unresolved_count,

            "potential_duplicate_count": potential_duplicate_count,

            "potential_duplicates": potential_duplicates,

            "reconciliation": reconciliation_result
        }

    except Exception:

        db.rollback()

        raise