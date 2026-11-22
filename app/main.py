from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    status,
    Query,
    UploadFile,
    File,
    Form
)

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, desc, func, and_

from typing import List, Optional
from pathlib import Path
from datetime import date

import tempfile
import hashlib


# --------------------------------------------------
# APPLICATION IMPORTS
# --------------------------------------------------

from app import services, crud

from app.database import get_db

from app.models import (
    FinancialProject,
    FinancialTransaction,
    ImportBatch,
    RejectedTransaction,
    Vendor,
    Category
)

from app.schemas import (
    FinancialProjectCreate,
    FinancialProjectResponse,
    FinancialProjectUpdate,
    FinancialProjectAnalytics,
    FinancialTransactionCreate,
    FinancialTransactionUpdate,
    FinancialTransactionResponse,
    ImportBatchResponse,
    RejectedTransactionResponse,
)

from app.ingestion.csv_loader import load_financial_csv
from app.validation.transaction_validator import validate_transactions
from app.ingestion.rejected_records import save_rejected_records
from app.ingestion.importer import import_financial_transactions

from app.ingestion.audit import (
    complete_import_batch,
    fail_import_batch
)


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="FinSight-AI API",
    description="Financial Project Management API",
    version="2.0.0"
)


# ==================================================
# 1. FINANCIAL PROJECT APIs
# ==================================================


# CREATE PROJECT

@app.post(
    "/projects/",
    response_model=FinancialProjectResponse,
    status_code=status.HTTP_201_CREATED
)
def create_project(
    project: FinancialProjectCreate,
    db: Session = Depends(get_db)
):
    return crud.create_project(db, project)


# GET ALL PROJECTS

@app.get(
    "/projects/",
    response_model=List[FinancialProjectResponse]
)
def read_projects(
    db: Session = Depends(get_db)
):
    return crud.get_projects(db)


# GET ONE PROJECT

@app.get(
    "/projects/{project_id}",
    response_model=FinancialProjectResponse
)
def read_project(
    project_id: int,
    db: Session = Depends(get_db)
):

    project = crud.get_project(db, project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial project not found"
        )

    return project


# UPDATE PROJECT

@app.patch(
    "/projects/{project_id}",
    response_model=FinancialProjectResponse
)
def update_project(
    project_id: int,
    project: FinancialProjectUpdate,
    db: Session = Depends(get_db)
):

    updated_data = project.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    if not updated_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field must be provided for updating"
        )

    updated_project = crud.update_project(
        db,
        project_id,
        updated_data
    )

    if updated_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial project not found"
        )

    return updated_project


# DELETE PROJECT

@app.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_project(
    project_id: int,
    db: Session = Depends(get_db)
):

    deleted = crud.delete_project(
        db,
        project_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial project not found"
        )

    return None


# PROJECT ANALYTICS

@app.get(
    "/projects/{project_id}/analytics",
    response_model=FinancialProjectAnalytics
)
def read_project_analytics(
    project_id: int,
    db: Session = Depends(get_db)
):

    project = crud.get_project(
        db,
        project_id
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return services.get_project_analytics(project)


# ==================================================
# 2. FINANCIAL TRANSACTION APIs
# ==================================================


# SEARCH TRANSACTIONS
# Keep this route before /transactions/{transaction_id}

@app.get("/transactions/search")
def search_transactions(
    transaction_type: Optional[str] = None,
    min_amount: Optional[float] = Query(default=None, ge=0),
    max_amount: Optional[float] = Query(default=None, ge=0),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):

    query = db.query(FinancialTransaction)

    if transaction_type:

        transaction_type = transaction_type.upper()

        if transaction_type not in ["EXPENSE", "INCOME"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid transaction type"
            )

        query = query.filter(
            FinancialTransaction.transaction_type == transaction_type
        )

    if min_amount is not None:

        query = query.filter(
            FinancialTransaction.amount >= min_amount
        )

    if max_amount is not None:

        query = query.filter(
            FinancialTransaction.amount <= max_amount
        )

    if min_amount is not None and max_amount is not None:

        if min_amount > max_amount:
            raise HTTPException(
                status_code=400,
                detail="Minimum amount cannot exceed maximum amount"
            )

    if start_date and end_date:

        if start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="Start date cannot be after end date"
            )

    if start_date:

        query = query.filter(
            FinancialTransaction.transaction_date >= start_date
        )

    if end_date:

        query = query.filter(
            FinancialTransaction.transaction_date <= end_date
        )

    transactions = (
        query
        .order_by(
            FinancialTransaction.transaction_date.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    return transactions


# CREATE TRANSACTION

@app.post(
    "/transactions/",
    response_model=FinancialTransactionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_transaction(
    transaction: FinancialTransactionCreate,
    db: Session = Depends(get_db)
):

    try:

        transaction_data = transaction.model_dump()

        return crud.create_transaction(
            db,
            transaction_data
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


# GET ALL TRANSACTIONS
# Includes pagination and transaction type filtering.

@app.get(
    "/transactions/",
    response_model=List[FinancialTransactionResponse]
)
def get_all_transactions(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    transaction_type: Optional[str] = Query(default=None),
    db: Session = Depends(get_db)
):

    query = db.query(FinancialTransaction)

    if transaction_type:

        transaction_type = transaction_type.upper()

        if transaction_type not in ["EXPENSE", "INCOME"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid transaction type"
            )

        query = query.filter(
            FinancialTransaction.transaction_type == transaction_type
        )

    transactions = (
        query
        .order_by(
            FinancialTransaction.transaction_date.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    return transactions


# GET ONE TRANSACTION

@app.get(
    "/transactions/{transaction_id}",
    response_model=FinancialTransactionResponse
)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):

    transaction = crud.get_transaction(
        db,
        transaction_id
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    return transaction


# GET PROJECT TRANSACTIONS

@app.get(
    "/projects/{project_id}/transactions",
    response_model=List[FinancialTransactionResponse]
)
def get_project_transactions(
    project_id: int,
    db: Session = Depends(get_db)
):

    project = db.get(
        FinancialProject,
        project_id
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return crud.get_project_transactions(
        db,
        project_id
    )


# UPDATE TRANSACTION

@app.patch(
    "/transactions/{transaction_id}",
    response_model=FinancialTransactionResponse
)
def update_transaction(
    transaction_id: int,
    transaction: FinancialTransactionUpdate,
    db: Session = Depends(get_db)
):

    update_data = transaction.model_dump(
        exclude_unset=True
    )

    try:

        updated_transaction = crud.update_transaction(
            db,
            transaction_id,
            update_data
        )

        if updated_transaction is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )

        return updated_transaction

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


# ==================================================
# 3. IMPORT BATCH APIs
# ==================================================


# GET ALL IMPORT BATCHES

@app.get(
    "/imports/",
    response_model=List[ImportBatchResponse]
)
def get_import_batches(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):

    statement = (
        select(ImportBatch)
        .order_by(desc(ImportBatch.created_at))
        .offset(skip)
        .limit(limit)
    )

    batches = db.scalars(statement).all()

    return batches


# GET ONE IMPORT BATCH

@app.get(
    "/imports/{batch_id}",
    response_model=ImportBatchResponse
)
def get_import_batch(
    batch_id: int,
    db: Session = Depends(get_db)
):

    batch = db.get(
        ImportBatch,
        batch_id
    )

    if batch is None:
        raise HTTPException(
            status_code=404,
            detail="Import batch not found"
        )

    return batch


# ==================================================
# 4. REJECTED TRANSACTION APIs
# ==================================================


# GET REJECTED TRANSACTIONS FOR A BATCH

@app.get(
    "/imports/{batch_id}/rejected",
    response_model=List[RejectedTransactionResponse]
)
def get_rejected_transactions(
    batch_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):

    batch = db.get(
        ImportBatch,
        batch_id
    )

    if batch is None:
        raise HTTPException(
            status_code=404,
            detail="Import batch not found"
        )

    statement = (
        select(RejectedTransaction)
        .where(
            RejectedTransaction.import_batch_id == batch_id
        )
        .order_by(
            RejectedTransaction.rejected_id
        )
        .offset(skip)
        .limit(limit)
    )

    records = db.scalars(statement).all()

    return records


# GET ONE REJECTED TRANSACTION

@app.get(
    "/rejected-transactions/{rejected_id}",
    response_model=RejectedTransactionResponse
)
def get_rejected_transaction(
    rejected_id: int,
    db: Session = Depends(get_db)
):

    record = db.get(
        RejectedTransaction,
        rejected_id
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Rejected transaction not found"
        )

    return record


# ==================================================
# 5. CSV FINANCIAL DATA INGESTION
# ==================================================


@app.post(
    "/imports/upload",
    response_model=ImportBatchResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_financial_csv(
    file: UploadFile = File(...),
    uploaded_by_employee_id: str = Form(...),
    uploaded_from_device_id: str = Form(...),
    db: Session = Depends(get_db)
):

    temp_file_path = None
    batch_id = None

    try:

        # STEP 1: Validate filename

        filename = Path(
            file.filename or ""
        ).name

        if not filename.lower().endswith(".csv"):

            raise HTTPException(
                status_code=400,
                detail="Only CSV files are allowed."
            )

        # STEP 2: Read uploaded file

        file_content = await file.read()

        if not file_content:

            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        # STEP 3: Validate file size

        max_file_size = 10 * 1024 * 1024

        if len(file_content) > max_file_size:

            raise HTTPException(
                status_code=413,
                detail="File size exceeds the 10 MB limit."
            )

        # STEP 4: Generate SHA-256 hash

        file_hash = hashlib.sha256(
            file_content
        ).hexdigest()

        # STEP 5: Check existing import batch

        existing_batch = db.scalar(
            select(ImportBatch).where(
                ImportBatch.file_hash == file_hash
            )
        )

        if existing_batch:

            # Completed files cannot be imported again
            if existing_batch.status == "COMPLETED":

                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"File already imported successfully. "
                        f"Batch ID: {existing_batch.batch_id}"
                    )
                )

            # Prevent simultaneous processing
            if existing_batch.status == "PROCESSING":

                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"This file is already being processed. "
                        f"Batch ID: {existing_batch.batch_id}"
                    )
                )

            # Allow retry of failed imports
            if existing_batch.status == "FAILED":

                existing_batch.status = "PROCESSING"

                existing_batch.imported_records = 0
                existing_batch.rejected_records = 0
                existing_batch.unresolved_vendor_count = 0
                existing_batch.total_records = 0

                existing_batch.error_message = None
                existing_batch.completed_at = None

                existing_batch.uploaded_by_employee_id = (
                    uploaded_by_employee_id
                )

                existing_batch.uploaded_from_device_id = (
                    uploaded_from_device_id
                )

                batch_id = existing_batch.batch_id

                db.commit()

            else:

                raise HTTPException(
                    status_code=409,
                    detail="Existing batch has an unsupported status."
                )

        else:

            # STEP 6: Create new import batch

            new_batch = ImportBatch(
                file_name=filename,
                file_hash=file_hash,
                uploaded_by_employee_id=uploaded_by_employee_id,
                uploaded_from_device_id=uploaded_from_device_id,
                total_records=0,
                imported_records=0,
                rejected_records=0,
                unresolved_vendor_count=0,
                status="PROCESSING"
            )

            db.add(new_batch)

            try:

                db.commit()

                db.refresh(new_batch)

                batch_id = new_batch.batch_id

            except IntegrityError:

                db.rollback()

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "This file was registered by another "
                        "upload request. Please check its batch status."
                    )
                )

        # STEP 7: Save CSV temporarily

        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=".csv",
            delete=False
        ) as temp_file:

            temp_file.write(file_content)

            temp_file_path = temp_file.name

        # STEP 8: Load CSV

        df = load_financial_csv(
            temp_file_path
        )

        # STEP 9: Validate transactions

        valid_df, rejected_df = validate_transactions(
            df,
            db
        )

        # STEP 10: Save rejected transactions

        rejected_count = save_rejected_records(
            db=db,
            rejected_df=rejected_df,
            batch_id=batch_id,
            rejection_stage="VALIDATION"
        )

        # STEP 11: Import valid transactions

        import_result = import_financial_transactions(
            valid_df,
            db,
            batch_id=batch_id
        )

        imported_count = import_result[
            "imported_transactions"
        ]

        unresolved_count = import_result[
            "unresolved_transactions"
        ]

        # STEP 12: Retrieve import batch

        batch = db.get(
            ImportBatch,
            batch_id
        )

        if batch is None:

            raise HTTPException(
                status_code=404,
                detail="Import batch not found."
            )

        # STEP 13: Update total records

        batch.total_records = len(df)

        # STEP 14: Mark batch as COMPLETED

        complete_import_batch(
            db=db,
            batch_id=batch_id,
            imported_records=imported_count,
            rejected_records=rejected_count,
            unresolved_vendor_count=unresolved_count
        )

        # STEP 15: Commit final batch changes

        db.commit()

        db.refresh(batch)

        return batch

    # --------------------------------------------------
    # ERROR HANDLING
    # --------------------------------------------------

    except HTTPException:

        db.rollback()

        if batch_id is not None:

            try:

                fail_import_batch(
                    db=db,
                    batch_id=batch_id,
                    error_message="Import processing failed"
                )

                db.commit()

            except Exception:

                db.rollback()

        raise

    except Exception as error:

        db.rollback()

        if batch_id is not None:

            try:

                fail_import_batch(
                    db=db,
                    batch_id=batch_id,
                    error_message=str(error)
                )

                db.commit()

            except Exception:

                db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"CSV processing failed: {str(error)}"
        )

    # --------------------------------------------------
    # TEMPORARY FILE CLEANUP
    # --------------------------------------------------

    finally:

        if temp_file_path and Path(temp_file_path).exists():

            Path(temp_file_path).unlink()

        await file.close()


# ==================================================
# 6. FINANCIAL ANALYTICS
# ==================================================


@app.get("/analytics/financial-summary")
def financial_summary(
    db: Session = Depends(get_db)
):

    # TOTAL EXPENSES

    total_expenses = (
        db.query(
            func.sum(FinancialTransaction.amount)
        )
        .filter(
            FinancialTransaction.transaction_type == "EXPENSE"
        )
        .scalar()
    )

    # TOTAL INCOME

    total_income = (
        db.query(
            func.sum(FinancialTransaction.amount)
        )
        .filter(
            FinancialTransaction.transaction_type == "INCOME"
        )
        .scalar()
    )

    # TOTAL TRANSACTIONS

    total_transactions = (
        db.query(
            func.count(
                FinancialTransaction.transaction_id
            )
        )
        .scalar()
    )

    # AVERAGE TRANSACTION

    average_transaction = (
        db.query(
            func.avg(FinancialTransaction.amount)
        )
        .scalar()
    )

    return {
        "total_expenses": float(total_expenses or 0),

        "total_income": float(total_income or 0),

        "net_balance": float(
            (total_income or 0) - (total_expenses or 0)
        ),

        "total_transactions": total_transactions,

        "average_transaction": float(
            average_transaction or 0
        )
    }

@app.get("/analytics/vendor-expenses")
def vendor_expense_summary(
    project_id: Optional[int] = Query(None, gt=0),
    db: Session = Depends(get_db)
):

    query = (
        db.query(
            Vendor.vendor_id,
            Vendor.vendor_name,
            func.sum(
                FinancialTransaction.amount
            ).label("total_expense"),
            func.count(
                FinancialTransaction.transaction_id
            ).label("transaction_count"),
            func.avg(
                FinancialTransaction.amount
            ).label("average_expense")
        )
        .join(
            FinancialTransaction,
            FinancialTransaction.vendor_id == Vendor.vendor_id
        )
        .filter(
            FinancialTransaction.transaction_type == "EXPENSE"
        )
    )

    # Optional project-wise filtering
    if project_id is not None:
        query = query.filter(
            FinancialTransaction.project_id == project_id
        )

    results = (
        query
        .group_by(
            Vendor.vendor_id,
            Vendor.vendor_name
        )
        .order_by(
            func.sum(FinancialTransaction.amount).desc()
        )
        .all()
    )

    return {
        "project_id": project_id,
        "vendor_expenses": [
            {
                "vendor_id": row.vendor_id,
                "vendor_name": row.vendor_name,
                "total_expense": float(row.total_expense or 0),
                "transaction_count": row.transaction_count,
                "average_expense": float(row.average_expense or 0)
            }
            for row in results
        ]
    }

@app.get("/analytics/category-expenses")
def category_expense_summary(
    project_id: Optional[int] = Query(None, gt=0),
    db: Session = Depends(get_db)
):

    query = (
        db.query(
            Category.category_id,
            Category.category_name,
            func.coalesce(
                func.sum(FinancialTransaction.amount), 0
            ).label("total_expense"),
            func.count(
                FinancialTransaction.transaction_id
            ).label("transaction_count"),
            func.avg(
                FinancialTransaction.amount
            ).label("average_expense")
        )
        .outerjoin(
            FinancialTransaction,
            and_(
                FinancialTransaction.category_id == Category.category_id,
                FinancialTransaction.transaction_type == "EXPENSE",
                *(
                    [FinancialTransaction.project_id == project_id]
                    if project_id is not None else []
                )
            )
        )
        .group_by(
            Category.category_id,
            Category.category_name
        )
        .order_by(
            func.sum(FinancialTransaction.amount).desc()
        )
    )

    results = query.all()

    return {
        "project_id": project_id,
        "category_expenses": [
            {
                "category_id": row.category_id,
                "category_name": row.category_name,
                "total_expense": float(row.total_expense or 0),
                "transaction_count": row.transaction_count,
                "average_expense": float(row.average_expense or 0)
            }
            for row in results
        ]
    }