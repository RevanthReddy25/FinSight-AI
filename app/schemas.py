from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from datetime import date,datetime
from typing import Literal,Any

class FinancialProjectCreate(BaseModel):
    """
    Schema for creating a new financial project.
    """

    project_name: str = Field(
        min_length=1,
        max_length=150
    )

    client_name: str = Field(
        min_length=1,
        max_length=150
    )

    budget: Decimal = Field(
        ge=0,
        max_digits=14,
        decimal_places=2
    )

    revenue: Decimal = Field(
        ge=0,
        max_digits=14,
        decimal_places=2
    )

    expenditure: Decimal = Field(
        ge=0,
        max_digits=14,
        decimal_places=2
    )


class FinancialProjectResponse(BaseModel):
    """
    Schema for returning financial project information.
    """

    model_config = ConfigDict(from_attributes=True)

    project_id: int
    project_name: str
    client_name: str
    budget: Decimal
    revenue: Decimal
    expenditure: Decimal

class FinancialProjectUpdate(BaseModel):
    """
    Schema for updating an existing financial project.
    All fields are optional.
    """

    project_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    client_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    budget: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=14,
        decimal_places=2
    )

    revenue: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=14,
        decimal_places=2
    )

    expenditure: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=14,
        decimal_places=2
    )

class FinancialProjectAnalytics(BaseModel):
    project_id: int
    project_name: str
    client_name: str
    budget: Decimal
    revenue: Decimal
    expenditure: Decimal
    profit: Decimal
    profit_margin: Decimal
    budget_utilization: Decimal
    budget_remaining: Decimal


class FinancialTransactionCreate(BaseModel):

    project_id: int = Field(gt=0)

    vendor_id: int | None = Field(default=None, gt=0)

    category_id: int = Field(gt=0)

    description: str = Field(min_length=3, max_length=500)

    amount: Decimal = Field(
        gt=0,
        max_digits=14,
        decimal_places=2
    )

    transaction_date: date

    transaction_type: Literal["EXPENSE", "INCOME"]

    status: Literal[
        "PENDING",
        "APPROVED",
        "REJECTED",
        "PAID"
    ] = "PENDING"


class FinancialTransactionUpdate(BaseModel):
    project_id: int | None = Field(default=None, gt=0)
    vendor_id: int | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)

    description: str | None = Field(
        default=None,
        min_length=3,
        max_length=500
    )

    amount: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=14,
        decimal_places=2
    )

    transaction_date: date | None = None

    transaction_type: Literal["EXPENSE", "INCOME"] | None = None

    status: Literal[
        "PENDING",
        "APPROVED",
        "REJECTED",
        "PAID"
    ] | None = None

class FinancialTransactionResponse(BaseModel):

    transaction_id: int

    project_id: int

    vendor_id: int | None

    category_id: int

    description: str

    amount: Decimal

    transaction_date: date

    transaction_type: str

    status: str

    model_config = ConfigDict(from_attributes=True)

class ImportBatchResponse(BaseModel):

    batch_id: int

    file_name: str
    file_hash: str

    uploaded_by_employee_id: str | None = None
    uploaded_from_device_id: str | None = None

    total_records: int
    imported_records: int
    rejected_records: int
    unresolved_vendor_count: int

    status: str

    uploaded_by: str | None = None
    error_message: str | None = None

    created_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class RejectedTransactionResponse(BaseModel):

    rejected_id: int
    import_batch_id: int

    source_row: int

    raw_data: dict[str, Any]
    errors: list[str]

    rejection_stage: str

    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)