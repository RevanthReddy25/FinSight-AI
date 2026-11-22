from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    JSON,
    DateTime,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    DateTime,
    func,
)
import pandas as pd
import numpy as np
from datetime import date, datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

from sqlalchemy import DateTime, func

# ==========================================
# 1. FINANCIAL PROJECT
# ==========================================

class FinancialProject(Base):

    __tablename__ = "financial_projects"

    __table_args__ = (
        CheckConstraint(
            "budget >= 0",
            name="ck_budget_nonnegative"
        ),
        CheckConstraint(
            "revenue >= 0",
            name="ck_revenue_nonnegative"
        ),
        CheckConstraint(
            "expenditure >= 0",
            name="ck_expenditure_nonnegative"
        ),
    )

    project_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    project_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    client_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    budget: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False
    )

    revenue: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False
    )

    expenditure: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False
    )

    # One project can have multiple transactions.
    transactions: Mapped[list["FinancialTransaction"]] = relationship(
        back_populates="project"
    )


# ==========================================
# 2. VENDOR
# ==========================================

class Vendor(Base):

    __tablename__ = "vendors"

    vendor_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    vendor_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True
    )

    gstin: Mapped[str | None] = mapped_column(
        String(15),
        nullable=True,
        unique=True
    )

    contact_email: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    vendor_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    transactions: Mapped[list["FinancialTransaction"]] = relationship(
        back_populates="vendor"
    )

# ==========================================
# 3. CATEGORY
# ==========================================

class Category(Base):

    __tablename__ = "categories"

    category_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    category_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    description: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True
    )

    # One category can contain multiple transactions.
    transactions: Mapped[list["FinancialTransaction"]] = relationship(
        back_populates="category"
    )


# ==========================================
# 4. FINANCIAL TRANSACTION
# ==========================================

class FinancialTransaction(Base):

    __tablename__ = "financial_transactions"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_transaction_amount_positive"
        ),
        CheckConstraint(
            "transaction_type IN ('EXPENSE', 'INCOME')",
            name="ck_transaction_type"
        ),
        CheckConstraint(
            "status IN ('PENDING', 'APPROVED', 'REJECTED', 'PAID')",
            name="ck_transaction_status"
        ),
        Index(
            "ix_transaction_project_date",
            "project_id",
            "transaction_date"
        ),
        Index(
            "ix_transaction_vendor_type",
            "vendor_id",
            "transaction_type"
        ),

        Index(
            "ix_transaction_type_date",
            "transaction_type",
            "transaction_date"
        ),
    )

    transaction_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey(
            "financial_projects.project_id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    vendor_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "vendors.vendor_id",
            ondelete="RESTRICT"
        ),
        nullable=True
    )

    vendor_name_raw: Mapped[str | None] = mapped_column(
    String(255),
    nullable=True
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey(
            "categories.category_id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    import_batch_id: Mapped[int | None] = mapped_column(
    ForeignKey("import_batches.batch_id"),
    nullable=True,
    index=True
    )

    import_batch = relationship(
    "ImportBatch",
    back_populates="transactions"
    )

    description: Mapped[str] = mapped_column(
        String(250),
        nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False
    )

    transaction_date: Mapped[Date] = mapped_column(
        Date,
        nullable=False
    )

    transaction_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING"
    )

    # ORM relationships

    project: Mapped["FinancialProject"] = relationship(
        back_populates="transactions"
    )

    vendor: Mapped["Vendor | None"] = relationship(
        back_populates="transactions"
    )

    category: Mapped["Category"] = relationship(
        back_populates="transactions"
    )

class UnresolvedVendor(Base):
    __tablename__ = "unresolved_vendors"

    unresolved_vendor_id = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    vendor_name_raw = mapped_column(
        String(255),
        nullable=False
    )

    normalized_vendor_name = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )

    gstin: Mapped[str | None] = mapped_column(
        String(15),
        nullable=True
    )

    occurrence_count = mapped_column(
        Integer,
        nullable=False,
        default=1
    )

    status = mapped_column(
        String(30),
        nullable=False,
        default="PENDING"
    )

    resolved_vendor_id = mapped_column(
        ForeignKey("vendors.vendor_id", ondelete="RESTRICT"),
        nullable=True
    )

    first_seen_at = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    last_seen_at = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    resolved_vendor = relationship("Vendor")

class ImportBatch(Base):
    __tablename__ = "import_batches"

    batch_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False
    )

    total_records: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    imported_records: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    rejected_records: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    unresolved_vendor_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="PROCESSING"
    )

    uploaded_by: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    uploaded_by_employee_id: Mapped[str | None] = mapped_column(
    String(50),
    nullable=True
    )

    uploaded_from_device_id: Mapped[str | None] = mapped_column(
    String(150),
    nullable=True
    )

    error_message: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True
    )

    created_at = mapped_column(
        DateTime,
        server_default=func.now()
    )

    completed_at = mapped_column(
        DateTime,
        nullable=True
    )

    # Relationship with FinancialTransaction
    transactions = relationship(
        "FinancialTransaction",
        back_populates="import_batch"
    )

    # Relationship with RejectedTransaction
    rejected_transactions = relationship(
        "RejectedTransaction",
        back_populates="import_batch"
    )

class RejectedTransaction(Base):
    __tablename__ = "rejected_transactions"

    __table_args__ = (
        UniqueConstraint(
            "import_batch_id",
            "source_row",
            name="uq_rejected_batch_source_row"
        ),
        CheckConstraint(
            "source_row > 0",
            name="ck_rejected_source_row_positive"
        ),
    )

    rejected_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    import_batch_id: Mapped[int] = mapped_column(
        ForeignKey("import_batches.batch_id"),
        nullable=False,
        index=True
    )

    source_row: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    raw_data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )

    errors: Mapped[list] = mapped_column(
        JSON,
        nullable=False
    )

    rejection_stage: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="VALIDATION"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    import_batch = relationship(
        "ImportBatch",
        back_populates="rejected_transactions"
    )

def make_json_safe(value):
    """
    Convert Pandas, NumPy, and Python values
    into JSON-serializable values.
    """

    if value is None:
        return None

    if isinstance(value, dict):
        return {
            key: make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [make_json_safe(item) for item in value]

    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        return None if np.isnan(value) else float(value)

    if isinstance(value, np.bool_):
        return bool(value)

    if pd.isna(value):
        return None

    return value