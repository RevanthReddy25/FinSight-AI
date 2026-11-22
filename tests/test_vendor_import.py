import pandas as pd

from app.models import (
    Vendor,
    Category,
    FinancialProject,
    FinancialTransaction,
    UnresolvedVendor
)

from app.ingestion.importer import (
    import_financial_transactions
)


def test_vendor_resolution_during_import(db_session):

    # ----------------------------------
    # 1. Create test project
    # ----------------------------------

    project = FinancialProject(
        project_name="Vendor Resolution Test",
        client_name="Test Client",
        budget=100000,
        revenue=150000,
        expenditure=0
    )

    db_session.add(project)

    # ----------------------------------
    # 2. Create test category
    # ----------------------------------

    category = Category(
        category_name="Cloud Services",
        description="Cloud infrastructure expenses"
    )

    db_session.add(category)

    # ----------------------------------
    # 3. Create existing vendor
    # ----------------------------------

    microsoft = Vendor(
        vendor_name="Microsoft"
    )

    db_session.add(microsoft)

    db_session.flush()

    # ----------------------------------
    # 4. Prepare incoming transactions
    # ----------------------------------

    data = [
        {
            "project_id": project.project_id,
            "vendor_id": "",
            "vendor_name": "Microsoft",
            "category_id": category.category_id,
            "description": "Software License",
            "amount": "25000.00",
            "transaction_date": "2026-11-01",
            "transaction_type": "EXPENSE",
            "status": "APPROVED"
        },
        {
            "project_id": project.project_id,
            "vendor_id": "",
            "vendor_name": "Google Cloud",
            "category_id": category.category_id,
            "description": "Cloud Hosting",
            "amount": "15000.00",
            "transaction_date": "2026-11-02",
            "transaction_type": "EXPENSE",
            "status": "PENDING"
        }
    ]

    df = pd.DataFrame(data)

    # ----------------------------------
    # 5. Import transactions
    # ----------------------------------

    result = import_financial_transactions(
        df,
        db_session
    )

    # ----------------------------------
    # 6. Verify import
    # ----------------------------------

    assert result["imported_transactions"] == 2

    transactions = db_session.query(
        FinancialTransaction
    ).order_by(
        FinancialTransaction.transaction_id
    ).all()

    assert len(transactions) == 2

    # Microsoft should be resolved
    assert transactions[0].vendor_id == microsoft.vendor_id

    # Google Cloud should remain unresolved
    assert transactions[1].vendor_id is None

    assert transactions[1].vendor_name_raw == "Google Cloud"

    # Verify unresolved queue
    unresolved = db_session.query(
        UnresolvedVendor
    ).filter_by(
        normalized_vendor_name="google cloud"
    ).first()

    assert unresolved is not None
    assert unresolved.status == "PENDING"

    assert unresolved.occurrence_count == 1