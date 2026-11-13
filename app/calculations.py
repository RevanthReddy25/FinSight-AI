from decimal import Decimal


def calculate_profit(
    revenue: Decimal,
    expenditure: Decimal
) -> Decimal:
    return revenue - expenditure


def calculate_profit_margin(
    revenue: Decimal,
    expenditure: Decimal
) -> Decimal:

    if revenue == 0:
        return Decimal("0.00")

    profit = calculate_profit(revenue, expenditure)

    return (profit / revenue) * Decimal("100")


def calculate_budget_utilization(
    budget: Decimal,
    expenditure: Decimal
) -> Decimal:

    if budget == 0:
        return Decimal("0.00")

    return (expenditure / budget) * Decimal("100")


def calculate_budget_remaining(
    budget: Decimal,
    expenditure: Decimal
) -> Decimal:

    return budget - expenditure