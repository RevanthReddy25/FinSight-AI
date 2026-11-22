import pandas as pd

from app.models import (
    FinancialProject,
    Vendor,
    Category
)

from app.validation.transaction_validator import (
    validate_transaction_row
)


def create_reference_data(db_session):

    # Create project
    project = FinancialProject(
        project_name="AI Financial Platform",
        client_name="Microsoft",
        budget=1000000,
        revenue=1500000,
        expenditure=500000
    )

    # Create vendor
    vendor = Vendor(
        vendor_name="Microsoft"
    )

    # Create category
    category = Category(
        category_name="Software Licensing",
        description="Software subscription expenses"
    )

    db_session.add_all([
        project,
        vendor,
        category
    ])

    db_session.flush()

    return project, vendor, category


def test_valid_transaction(db_session):

    project, vendor, category = create_reference_data(
        db_session
    )

    row = pd.Series({
        "project_id": str(project.project_id),
        "vendor_id": str(vendor.vendor_id),
        "category_id": str(category.category_id),
        "description": "Microsoft subscription",
        "amount": "25000.00",
        "transaction_date": "2026-11-01",
        "transaction_type": "EXPENSE",
        "status": "PENDING"
    })

    errors = validate_transaction_row(
        row,
        db_session
    )

    assert errors == []


def test_invalid_amount(db_session):

    project, vendor, category = create_reference_data(
        db_session
    )

    row = pd.Series({
        "project_id": str(project.project_id),
        "vendor_id": str(vendor.vendor_id),
        "category_id": str(category.category_id),
        "description": "Microsoft subscription",
        "amount": "-25000.00",
        "transaction_date": "2026-11-01",
        "transaction_type": "EXPENSE",
        "status": "PENDING"
    })

    errors = validate_transaction_row(
        row,
        db_session
    )

    assert any(
        "Amount" in error
        for error in errors
    )


def test_invalid_vendor(db_session):

    project, vendor, category = create_reference_data(
        db_session
    )

    row = pd.Series({
        "project_id": str(project.project_id),
        "vendor_id": "9999",
        "category_id": str(category.category_id),
        "description": "Microsoft subscription",
        "amount": "25000.00",
        "transaction_date": "2026-11-01",
        "transaction_type": "EXPENSE",
        "status": "PENDING"
    })

    errors = validate_transaction_row(
        row,
        db_session
    )

    assert any(
        "Vendor" in error and "does not exist" in error
        for error in errors
    )