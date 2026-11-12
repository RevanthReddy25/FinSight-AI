from decimal import Decimal

from app.models import FinancialProject


project = FinancialProject(
    project_id=1,
    project_name="Banking Analytics Platform",
    client_name="ABC Financial Services",
    budget=Decimal("1000000"),
    revenue=Decimal("1200000"),
    expenditure=Decimal("800000"),
)

print("Project Name:", project.project_name)
print("Client:", project.client_name)
print("Budget:", project.budget)
print("Revenue:", project.revenue)
print("Expenditure:", project.expenditure)