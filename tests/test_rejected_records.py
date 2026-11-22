import pandas as pd

from app.ingestion.rejected_records import (
    save_rejected_records
)

from app.models import ImportBatch, RejectedTransaction


def test_save_rejected_records(db_session):

    batch = ImportBatch(
        file_name="transactions.csv",
        file_hash="test_rejected_hash_001",
        total_records=2,
        status="PROCESSING"
    )

    db_session.add(batch)
    db_session.flush()

    rejected_df = pd.DataFrame([
        {
            "source_row": 3,
            "project_id": "1",
            "vendor_name": "AWS",
            "amount": "-4500",
            "transaction_date": "2026-11-02",
            "errors": [
                "Amount must be greater than zero"
            ]
        },
        {
            "source_row": 4,
            "project_id": "1",
            "vendor_name": "Google Cloud",
            "amount": "15000",
            "transaction_date": "invalid-date",
            "errors": [
                "Invalid transaction date"
            ]
        }
    ])

    count = save_rejected_records(
        db=db_session,
        rejected_df=rejected_df,
        batch_id=batch.batch_id
    )

    db_session.commit()

    assert count == 2

    records = (
        db_session.query(RejectedTransaction)
        .filter_by(import_batch_id=batch.batch_id)
        .all()
    )

    assert len(records) == 2

    assert records[0].source_row == 3
    assert records[0].raw_data["amount"] == "-4500"

    assert (
        "Amount must be greater than zero"
        in records[0].errors
    )