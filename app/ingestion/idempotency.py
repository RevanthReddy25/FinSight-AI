import hashlib

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import ImportBatch


def calculate_file_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        for chunk in iter(
            lambda: file.read(4096),
            b""
        ):
            sha256.update(chunk)

    return sha256.hexdigest()


def check_existing_batch(
    db: Session,
    file_hash: str
):

    return db.scalar(
        select(ImportBatch).where(
            ImportBatch.file_hash == file_hash
        )
    )


def register_import_batch(
    db: Session,
    file_path: str,
    file_hash: str,
    total_records: int
):

    existing_batch = check_existing_batch(
        db,
        file_hash
    )

    if existing_batch:

        return {
            "is_duplicate": True,
            "batch_id": existing_batch.batch_id,
            "message": "This file has already been imported."
        }

    batch = ImportBatch(
        file_name=file_path.split("\\")[-1],
        file_hash=file_hash,
        total_records=total_records,
        status="PROCESSING"
    )

    db.add(batch)

    db.flush()

    return {
        "is_duplicate": False,
        "batch_id": batch.batch_id,
        "message": "New import batch registered."
    }