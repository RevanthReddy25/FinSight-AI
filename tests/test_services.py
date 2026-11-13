from decimal import Decimal

from app.models import FinancialProject
from app.services import get_project_analytics


def create_sample_project():
    return FinancialProject(
        project_id=2,
        project_name="Investment Analytics",
        client_name="XYZ Financial Services",
        budget=Decimal("750000.00"),
        revenue=Decimal("680000.00"),
        expenditure=Decimal("420000.00")
    )


def test_get_project_analytics():
    project = create_sample_project()

    result = get_project_analytics(project)

    # Verify project information
    assert result.project_id == 2
    assert result.project_name == "Investment Analytics"
    assert result.client_name == "XYZ Financial Services"

    # Verify financial calculations
    assert result.profit == Decimal("260000.00")
    assert result.profit_margin == Decimal("38.24")

    assert result.budget_utilization == Decimal("56.00")
    assert result.budget_remaining == Decimal("330000.00")

from app.services import round_financial_value


def test_round_financial_value():
    assert round_financial_value(
        Decimal("38.235")
    ) == Decimal("38.24")

    assert round_financial_value(
        Decimal("56.004")
    ) == Decimal("56.00")

    assert round_financial_value(
        Decimal("12.999")
    ) == Decimal("13.00")

def test_get_project_analytics_with_zero_values():
    project = FinancialProject(
        project_id=3,
        project_name="New Project",
        client_name="ABC Finance",
        budget=Decimal("0.00"),
        revenue=Decimal("0.00"),
        expenditure=Decimal("0.00")
    )

    result = get_project_analytics(project)

    assert result.profit == Decimal("0.00")
    assert result.profit_margin == Decimal("0.00")
    assert result.budget_utilization == Decimal("0.00")
    assert result.budget_remaining == Decimal("0.00")