import hashlib
import io

import pandas as pd
import pytest

from sqlalchemy import select

from app.main import app
from app.models import ImportBatch


TEST_EMPLOYEE_ID = "EMP001"
TEST_DEVICE_ID = "DEVICE001"


VALID_CSV = b"""project_id,vendor_id,vendor_name,category_id,description,amount,transaction_date,transaction_type,status
1,,Microsoft,1,Software License Subscription,25000.00,2026-11-01,EXPENSE,APPROVED
"""


def upload_file(
    client,
    content=VALID_CSV,
    filename="transactions.csv"
):

    return client.post(
        "/imports/upload",
        files={
            "file": (
                filename,
                io.BytesIO(content),
                "text/csv"
            )
        },
        data={
            "uploaded_by_employee_id": TEST_EMPLOYEE_ID,
            "uploaded_from_device_id": TEST_DEVICE_ID
        }
    )


def setup_successful_processing(monkeypatch):

    import app.main as main

    monkeypatch.setattr(
        main,
        "load_financial_csv",
        lambda path: pd.DataFrame([
            {
                "project_id": 1,
                "vendor_id": None,
                "vendor_name": "Microsoft",
                "category_id": 1,
                "description": "Software License Subscription",
                "amount": "25000.00",
                "transaction_date": "2026-11-01",
                "transaction_type": "EXPENSE",
                "status": "APPROVED"
            }
        ])
    )

    monkeypatch.setattr(
        main,
        "validate_transactions",
        lambda df, db: (df, pd.DataFrame())
    )

    monkeypatch.setattr(
        main,
        "save_rejected_records",
        lambda **kwargs: 0
    )

    monkeypatch.setattr(
        main,
        "import_financial_transactions",
        lambda *args, **kwargs: {
            "imported_transactions": 1,
            "resolved_vendors": 1,
            "unresolved_transactions": 0,
            "potential_duplicate_count": 0,
            "potential_duplicates": [],
            "reconciliation": {
                "resolved_vendors": 0,
                "updated_transactions": 0
            }
        }
    )

    def mock_complete_import_batch(
        db,
        batch_id,
        imported_records,
        rejected_records,
        unresolved_vendor_count
    ):

        batch = db.get(ImportBatch, batch_id)

        batch.status = "COMPLETED"
        batch.imported_records = imported_records
        batch.rejected_records = rejected_records
        batch.unresolved_vendor_count = unresolved_vendor_count

    monkeypatch.setattr(
        main,
        "complete_import_batch",
        mock_complete_import_batch
    )


# --------------------------------------------------
# TEST 1: Successful CSV upload
# --------------------------------------------------

def test_successful_csv_upload(
    client,
    db_session,
    monkeypatch
):

    setup_successful_processing(monkeypatch)

    response = upload_file(client)

    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "COMPLETED"
    assert data["file_name"] == "transactions.csv"
    assert data["imported_records"] == 1

    batch = db_session.scalars(
        select(ImportBatch)
    ).first()

    assert batch is not None
    assert batch.status == "COMPLETED"

    print("PASS: Successful CSV upload")


# --------------------------------------------------
# TEST 2: Invalid file extension
# --------------------------------------------------

def test_invalid_file_extension(client):

    response = upload_file(
        client,
        filename="transactions.xlsx"
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Only CSV files are allowed."
    )

    print("PASS: Invalid file extension")


# --------------------------------------------------
# TEST 3: Empty CSV file
# --------------------------------------------------

def test_empty_file(client):

    response = upload_file(
        client,
        content=b""
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Uploaded file is empty."
    )

    print("PASS: Empty file validation")


# --------------------------------------------------
# TEST 4: File exceeding 10 MB
# --------------------------------------------------

def test_file_size_exceeded(client):

    large_content = b"a" * (10 * 1024 * 1024 + 1)

    response = upload_file(
        client,
        content=large_content
    )

    assert response.status_code == 413

    assert response.json()["detail"] == (
        "File size exceeds the 10 MB limit."
    )

    print("PASS: File size validation")


# --------------------------------------------------
# TEST 5: Duplicate completed upload
# --------------------------------------------------

def test_duplicate_completed_upload(
    client,
    db_session
):

    file_hash = hashlib.sha256(
        VALID_CSV
    ).hexdigest()

    batch = ImportBatch(
        file_name="transactions.csv",
        file_hash=file_hash,
        uploaded_by_employee_id=TEST_EMPLOYEE_ID,
        uploaded_from_device_id=TEST_DEVICE_ID,
        status="COMPLETED",
        total_records=1,
        imported_records=1,
        rejected_records=0,
        unresolved_vendor_count=0
    )

    db_session.add(batch)
    db_session.commit()

    response = upload_file(client)

    assert response.status_code == 409

    assert "already imported successfully" in (
        response.json()["detail"]
    )

    print("PASS: Completed duplicate upload blocked")


# --------------------------------------------------
# TEST 6: Duplicate processing upload
# --------------------------------------------------

def test_duplicate_processing_upload(
    client,
    db_session
):

    file_hash = hashlib.sha256(
        VALID_CSV
    ).hexdigest()

    batch = ImportBatch(
        file_name="transactions.csv",
        file_hash=file_hash,
        uploaded_by_employee_id=TEST_EMPLOYEE_ID,
        uploaded_from_device_id=TEST_DEVICE_ID,
        status="PROCESSING"
    )

    db_session.add(batch)
    db_session.commit()

    response = upload_file(client)

    assert response.status_code == 409

    assert "already being processed" in (
        response.json()["detail"]
    )

    print("PASS: Concurrent processing protection")


# --------------------------------------------------
# TEST 7: Failed batch retry
# --------------------------------------------------

def test_failed_batch_retry(
    client,
    db_session,
    monkeypatch
):

    setup_successful_processing(monkeypatch)

    file_hash = hashlib.sha256(
        VALID_CSV
    ).hexdigest()

    batch = ImportBatch(
        file_name="transactions.csv",
        file_hash=file_hash,
        uploaded_by_employee_id="OLD_EMPLOYEE",
        uploaded_from_device_id="OLD_DEVICE",
        status="FAILED",
        total_records=1,
        imported_records=0,
        rejected_records=0,
        unresolved_vendor_count=0,
        error_message="Previous import failed"
    )

    db_session.add(batch)
    db_session.commit()

    original_batch_id = batch.batch_id

    response = upload_file(client)

    assert response.status_code == 201

    db_session.refresh(batch)

    assert batch.batch_id == original_batch_id
    assert batch.status == "COMPLETED"

    assert batch.uploaded_by_employee_id == TEST_EMPLOYEE_ID
    assert batch.uploaded_from_device_id == TEST_DEVICE_ID

    print("PASS: Failed batch retry")


# --------------------------------------------------
# TEST 8: Audit information
# --------------------------------------------------

def test_audit_information(
    client,
    db_session,
    monkeypatch
):

    setup_successful_processing(monkeypatch)

    response = upload_file(client)

    assert response.status_code == 201

    batch = db_session.scalars(
        select(ImportBatch)
    ).first()

    assert batch.uploaded_by_employee_id == TEST_EMPLOYEE_ID

    assert batch.uploaded_from_device_id == TEST_DEVICE_ID

    assert batch.file_hash == hashlib.sha256(
        VALID_CSV
    ).hexdigest()

    assert batch.created_at is not None

    print("PASS: Import audit information")


# --------------------------------------------------
# TEST 9: Import processing failure
# --------------------------------------------------

def test_import_processing_failure(
    client,
    db_session,
    monkeypatch
):

    import app.main as main

    monkeypatch.setattr(
        main,
        "load_financial_csv",
        lambda path: pd.DataFrame([
            {"description": "Test transaction"}
        ])
    )

    def fail_validation(df, db):
        raise ValueError("Simulated validation failure")

    monkeypatch.setattr(
        main,
        "validate_transactions",
        fail_validation
    )

    response = upload_file(client)

    assert response.status_code == 500

    batch = db_session.scalars(
        select(ImportBatch)
    ).first()

    assert batch is not None
    assert batch.status == "FAILED"

    assert "Simulated validation failure" in (
        batch.error_message
    )

    print("PASS: Failed import handling")