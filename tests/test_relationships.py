
from decimal import Decimal
from datetime import date

from app.database import SessionLocal
from app.models import (
    FinancialProject,
    Vendor,
    Category,
    FinancialTransaction
)


def get_or_create_project(db):
    """Retrieve an existing project or create a new one."""

    project = (
        db.query(FinancialProject)
        .filter(
            FinancialProject.project_name == "Banking AI Platform"
        )
        .first()
    )

    if project is None:
        project = FinancialProject(
            project_name="Banking AI Platform",
            client_name="ABC Bank",
            budget=Decimal("500000.00"),
            revenue=Decimal("750000.00"),
            expenditure=Decimal("0.00")
        )

        db.add(project)
        db.flush()

        print("New project created.")

    else:
        print("Existing project found.")

    return project


def get_or_create_vendor(db, vendor_name, email, vendor_type):
    """Retrieve an existing vendor or create a new one."""

    vendor = (
        db.query(Vendor)
        .filter(Vendor.vendor_name == vendor_name)
        .first()
    )

    if vendor is None:
        vendor = Vendor(
            vendor_name=vendor_name,
            contact_email=email,
            vendor_type=vendor_type
        )

        db.add(vendor)
        db.flush()

        print(f"New vendor created: {vendor_name}")

    else:
        print(f"Existing vendor found: {vendor_name}")

    return vendor


def get_or_create_category(db, category_name, description):
    """Retrieve an existing category or create a new one."""

    category = (
        db.query(Category)
        .filter(Category.category_name == category_name)
        .first()
    )

    if category is None:
        category = Category(
            category_name=category_name,
            description=description
        )

        db.add(category)
        db.flush()

        print(f"New category created: {category_name}")

    else:
        print(f"Existing category found: {category_name}")

    return category


def create_transaction(
    db,
    project,
    vendor,
    category,
    description,
    amount,
    transaction_date,
    transaction_type="EXPENSE",
    status="APPROVED"
):
    """Create a transaction unless the same test transaction exists."""

    existing_transaction = (
        db.query(FinancialTransaction)
        .filter(
            FinancialTransaction.project_id == project.project_id,
            FinancialTransaction.vendor_id == vendor.vendor_id,
            FinancialTransaction.category_id == category.category_id,
            FinancialTransaction.description == description,
            FinancialTransaction.amount == amount,
            FinancialTransaction.transaction_date == transaction_date
        )
        .first()
    )

    if existing_transaction is not None:
        print(f"Transaction already exists: {description}")
        return existing_transaction

    transaction = FinancialTransaction(
        project_id=project.project_id,
        vendor_id=vendor.vendor_id,
        category_id=category.category_id,
        description=description,
        amount=amount,
        transaction_date=transaction_date,
        transaction_type=transaction_type,
        status=status
    )

    db.add(transaction)
    db.flush()

    print(f"Transaction created: {description}")

    return transaction


def display_transactions(db):
    """Display transactions with their related records."""

    transactions = (
        db.query(FinancialTransaction)
        .order_by(FinancialTransaction.transaction_id)
        .all()
    )

    print("\n========== FINANCIAL TRANSACTIONS ==========\n")

    for transaction in transactions:

        print("Transaction ID:", transaction.transaction_id)

        print("Project:", transaction.project.project_name)

        print(
            "Vendor:",
            transaction.vendor.vendor_name
            if transaction.vendor else "Not specified"
        )

        print("Category:", transaction.category.category_name)

        print("Description:", transaction.description)

        print("Amount:", transaction.amount)

        print("Type:", transaction.transaction_type)

        print("Status:", transaction.status)

        print("Date:", transaction.transaction_date)

        print("--------------------------------------------")


def display_total_expenditure(db):
    """Calculate total approved and paid expenses."""

    from sqlalchemy import func

    total = (
        db.query(func.sum(FinancialTransaction.amount))
        .filter(
            FinancialTransaction.transaction_type == "EXPENSE",
            FinancialTransaction.status.in_(["APPROVED", "PAID"])
        )
        .scalar()
    )

    total = total if total is not None else Decimal("0.00")

    print("\n========== FINANCIAL SUMMARY ==========")

    print("Total Approved/Paid Expenditure:", total)


def main():

    db = SessionLocal()

    try:

        # 1. Create or retrieve project
        project = get_or_create_project(db)

        # 2. Create or retrieve vendors
        microsoft = get_or_create_vendor(
            db,
            "Microsoft",
            "finance@microsoft.com",
            "Technology"
        )

        aws = get_or_create_vendor(
            db,
            "AWS",
            "finance@aws.com",
            "Cloud Services"
        )

        google = get_or_create_vendor(
            db,
            "Google",
            "finance@google.com",
            "Technology"
        )

        # 3. Create or retrieve categories
        software = get_or_create_category(
            db,
            "Software Licensing",
            "Software subscriptions and licenses"
        )

        cloud = get_or_create_category(
            db,
            "Cloud Infrastructure",
            "Cloud hosting and infrastructure expenses"
        )

        # 4. Create transactions
        create_transaction(
            db,
            project,
            microsoft,
            software,
            "Microsoft software licensing",
            Decimal("25000.00"),
            date.today()
        )

        create_transaction(
            db,
            project,
            aws,
            cloud,
            "AWS cloud infrastructure expenses",
            Decimal("45000.00"),
            date.today()
        )

        create_transaction(
            db,
            project,
            google,
            software,
            "Google software licensing",
            Decimal("15000.00"),
            date.today()
        )

        # 5. Commit all database changes
        db.commit()

        print("\nAll database operations completed successfully.")

        # 6. Display transactions
        display_transactions(db)

        # 7. Display financial summary
        display_total_expenditure(db)

    except Exception as error:

        db.rollback()

        print("\nAn error occurred:", error)

        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()
