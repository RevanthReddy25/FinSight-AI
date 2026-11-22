from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import ImportBatch


def complete_import_batch(
    db: Session,
    batch_id: int,
    imported_records: int,
    rejected_records: int,
    unresolved_vendor_count: int
):
    batch = db.get(ImportBatch, batch_id)

    if not batch:
        raise ValueError("Import batch not found.")

    batch.imported_records = imported_records
    batch.rejected_records = rejected_records
    batch.unresolved_vendor_count = unresolved_vendor_count

    batch.status = "COMPLETED"
    batch.completed_at = datetime.now(timezone.utc)

    db.flush()

    return batch

def fail_import_batch(
    db: Session,
    batch_id: int,
    error_message: str
):
    batch = db.get(ImportBatch, batch_id)

    if not batch:
        raise ValueError("Import batch not found.")

    batch.status = "FAILED"
    batch.error_message = error_message[:2000]
    batch.completed_at = datetime.now(timezone.utc)

    db.flush()

    return batch