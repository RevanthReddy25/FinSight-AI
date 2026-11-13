from decimal import Decimal

from sqlalchemy import CheckConstraint, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FinancialProject(Base):
    """
    SQLAlchemy model representing a business project's
    financial information.
    """

    __tablename__ = "financial_projects"

    __table_args__ = (
        CheckConstraint("budget >= 0", name="ck_budget_nonnegative"),
        CheckConstraint("revenue >= 0", name="ck_revenue_nonnegative"),
        CheckConstraint(
            "expenditure >= 0",
            name="ck_expenditure_nonnegative"
        ),
    )

    project_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
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