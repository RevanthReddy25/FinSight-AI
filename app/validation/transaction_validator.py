from decimal import Decimal, InvalidOperation
from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from app.models import FinancialProject, Vendor, Category


VALID_TRANSACTION_TYPES = {
    "EXPENSE",
    "INCOME"
}

VALID_STATUSES = {
    "PENDING",
    "APPROVED",
    "REJECTED",
    "PAID"
}

def clean_value(value):
    """Convert missing Pandas values into an empty string."""
    if pd.isna(value):
        return ""

    return str(value).strip()

def validate_transaction_row(
    row,
    db: Session
):
    errors = []

    # 1. Validate project_id
    try:
        project_id = int(row["project_id"])

        if project_id <= 0:
            errors.append("Project ID must be positive")

        elif db.get(FinancialProject, project_id) is None:
            errors.append("Project does not exist")

    except (ValueError, TypeError):
        errors.append("Invalid project ID")

    # 2. Validate vendor_id

    vendor_id_value = clean_value(row.get("vendor_id"))

    if vendor_id_value:

        try:
            vendor_id = int(vendor_id_value)

            if vendor_id <= 0:
                errors.append("Vendor ID must be positive.")

            elif db.get(Vendor, vendor_id) is None:
                errors.append(
                    f"Vendor ID {vendor_id} does not exist."
            )

        except (ValueError, TypeError):
            errors.append("Vendor ID must be a valid integer.")

    # 3. Validate category_id
    try:
        category_id = int(row["category_id"])

        if category_id <= 0:
            errors.append("Category ID must be positive")

        elif db.get(Category, category_id) is None:
            errors.append("Category does not exist")

    except (ValueError, TypeError):
        errors.append("Invalid category ID")

    vendor_name = clean_value(row.get("vendor_name"))

    if len(vendor_name) > 255:
        errors.append("Vendor name cannot exceed 255 characters.")

    # 4. Validate description
    description = clean_value(row.get("description"))

    if not description:
        errors.append("Description cannot be empty")

    elif len(description) > 500:
        errors.append("Description exceeds 500 characters")

    # 5. Validate amount
    try:
        amount = Decimal(str(row["amount"]).strip())

        if not amount.is_finite():
            errors.append("Amount must be a finite number")

        elif amount <= 0:
            errors.append("Amount must be greater than zero")

        elif amount.as_tuple().exponent < -2:
            errors.append("Amount cannot have more than 2 decimal places")

        elif len(amount.as_tuple().digits) > 14:
            errors.append("Amount exceeds maximum precision")

    except (InvalidOperation, ValueError, TypeError):
        errors.append("Invalid financial amount")

    # 6. Validate transaction date
    try:
        transaction_date = date.fromisoformat(
            str(row["transaction_date"]).strip()
        )

    except (ValueError, TypeError):
        errors.append("Invalid transaction date")

    # 7. Validate transaction type
    transaction_type = clean_value(
        row.get("transaction_type")
    ).upper()

    if transaction_type not in VALID_TRANSACTION_TYPES:
        errors.append("Invalid transaction type")

    # 8. Validate status
    status = clean_value(
        row.get("status")
    ).upper()

    if status not in VALID_STATUSES:
        errors.append("Invalid transaction status")

    return errors

def validate_transactions(
    df: pd.DataFrame,
    db: Session
):
    valid_records = []
    rejected_records = []

    for _, row in df.iterrows():

        errors = validate_transaction_row(row, db)

        record = row.to_dict()

        if errors:
            record["errors"] = errors
            rejected_records.append(record)

        else:
            valid_records.append(record)

    valid_df = pd.DataFrame(valid_records)
    rejected_df = pd.DataFrame(rejected_records)

    return valid_df, rejected_df