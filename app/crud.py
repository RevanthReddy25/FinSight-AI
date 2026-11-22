from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FinancialProject
from app.schemas import FinancialProjectCreate

from app.models import (
    FinancialTransaction,
    FinancialProject,
    Vendor,
    Category,
)


# 1. CREATE
def create_project(
    db: Session,
    project: FinancialProjectCreate
) -> FinancialProject:

    db_project = FinancialProject(
        project_name=project.project_name,
        client_name=project.client_name,
        budget=project.budget,
        revenue=project.revenue,
        expenditure=project.expenditure
    )

    try:
        db.add(db_project)
        db.commit()
        db.refresh(db_project)

    except Exception:
        db.rollback()
        raise

    return db_project


# 2. READ ALL
def get_projects(
    db: Session
) -> list[FinancialProject]:

    statement = select(FinancialProject)

    return list(db.scalars(statement).all())


# 3. READ ONE
def get_project(
    db: Session,
    project_id: int
) -> FinancialProject | None:

    statement = select(FinancialProject).where(
        FinancialProject.project_id == project_id
    )

    return db.scalar(statement)


# 4. UPDATE
def update_project(
    db: Session,
    project_id: int,
    updated_data: dict
) -> FinancialProject | None:

    db_project = get_project(db, project_id)

    if db_project is None:
        return None

    for field, value in updated_data.items():
        setattr(db_project, field, value)

    try:
        db.commit()
        db.refresh(db_project)

    except Exception:
        db.rollback()
        raise

    return db_project


# 5. DELETE
def delete_project(
    db: Session,
    project_id: int
) -> bool:

    db_project = get_project(db, project_id)

    if db_project is None:
        return False

    try:
        db.delete(db_project)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return True

def create_transaction(
    db: Session,
    transaction_data: dict
) -> FinancialTransaction:

    try:
        # Check whether project exists
        project = db.get(
            FinancialProject,
            transaction_data["project_id"]
        )

        if project is None:
            raise ValueError("Project does not exist")

        # Check whether vendor exists, if supplied
        vendor_id = transaction_data.get("vendor_id")

        if vendor_id is not None:
            vendor = db.get(Vendor, vendor_id)

            if vendor is None:
                raise ValueError("Vendor does not exist")

        # Check whether category exists
        category = db.get(
            Category,
            transaction_data["category_id"]
        )

        if category is None:
            raise ValueError("Category does not exist")

        # Create transaction object
        transaction = FinancialTransaction(
            **transaction_data
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction

    except Exception:
        db.rollback()
        raise

def get_transaction(
    db: Session,
    transaction_id: int
):
    return db.get(FinancialTransaction, transaction_id)

def get_all_transactions(db: Session):
    statement = select(FinancialTransaction)

    return db.scalars(statement).all()

def update_transaction(
    db: Session,
    transaction_id: int,
    update_data: dict
):
    transaction = db.get(
        FinancialTransaction,
        transaction_id
    )

    if transaction is None:
        return None

    try:
        # Validate project
        if "project_id" in update_data:
            project = db.get(
                FinancialProject,
                update_data["project_id"]
            )

            if project is None:
                raise ValueError("Project does not exist")

        # Validate vendor
        if "vendor_id" in update_data:
            vendor_id = update_data["vendor_id"]

            if vendor_id is not None:
                vendor = db.get(Vendor, vendor_id)

                if vendor is None:
                    raise ValueError("Vendor does not exist")

        # Validate category
        if "category_id" in update_data:
            category = db.get(
                Category,
                update_data["category_id"]
            )

            if category is None:
                raise ValueError("Category does not exist")

        # Update all submitted fields
        for field, value in update_data.items():
            setattr(transaction, field, value)

        db.commit()
        db.refresh(transaction)

        return transaction

    except Exception:
        db.rollback()
        raise


def get_project_transactions(
    db: Session,
    project_id: int
):
    statement = select(FinancialTransaction).where(
        FinancialTransaction.project_id == project_id
    )

    return db.scalars(statement).all()