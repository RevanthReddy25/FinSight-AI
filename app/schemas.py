from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


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