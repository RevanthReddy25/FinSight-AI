from app.calculations import (
    calculate_profit,
    calculate_profit_margin,
    calculate_budget_utilization,
    calculate_budget_remaining,
)
from app.models import FinancialProject
from app.schemas import FinancialProjectAnalytics

from decimal import Decimal, ROUND_HALF_UP

def round_financial_value(value: Decimal) -> Decimal:
    return value.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

def get_project_analytics(
    project: FinancialProject
) -> FinancialProjectAnalytics:

    profit = calculate_profit(
        project.revenue,
        project.expenditure
    )

    return FinancialProjectAnalytics(
        project_id=project.project_id,
        project_name=project.project_name,
        client_name=project.client_name,
        budget=project.budget,
        revenue=project.revenue,
        expenditure=project.expenditure,
        profit=profit,
        profit_margin=round_financial_value(
    calculate_profit_margin(
        project.revenue,
        project.expenditure
    )
),

budget_utilization=round_financial_value(
    calculate_budget_utilization(
        project.budget,
        project.expenditure
    )
),



        budget_remaining=calculate_budget_remaining(
            project.budget,
            project.expenditure
        )
    )
