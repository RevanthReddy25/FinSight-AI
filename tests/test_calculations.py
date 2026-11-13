from decimal import Decimal

from app.calculations import (
    calculate_profit,
    calculate_profit_margin,
    calculate_budget_utilization,
    calculate_budget_remaining
)


# TEST 1: PROFIT CALCULATION
def test_calculate_profit():

    revenue = Decimal("1200000.00")
    expenditure = Decimal("700000.00")

    result = calculate_profit(revenue, expenditure)

    assert result == Decimal("500000.00")


# TEST 2: NEGATIVE PROFIT
def test_calculate_negative_profit():

    revenue = Decimal("500000.00")
    expenditure = Decimal("700000.00")

    result = calculate_profit(revenue, expenditure)

    assert result == Decimal("-200000.00")


# TEST 3: PROFIT MARGIN
def test_calculate_profit_margin():

    revenue = Decimal("1200000.00")
    expenditure = Decimal("700000.00")

    result = calculate_profit_margin(revenue, expenditure)

    assert abs(result - Decimal("41.6667")) < Decimal("0.0001")


# TEST 4: ZERO REVENUE
def test_profit_margin_zero_revenue():

    revenue = Decimal("0.00")
    expenditure = Decimal("50000.00")

    result = calculate_profit_margin(revenue, expenditure)

    assert result == Decimal("0.00")


# TEST 5: BUDGET UTILIZATION
def test_calculate_budget_utilization():

    budget = Decimal("1000000.00")
    expenditure = Decimal("700000.00")

    result = calculate_budget_utilization(budget, expenditure)

    assert result == Decimal("70.00")


# TEST 6: ZERO BUDGET
def test_budget_utilization_zero_budget():

    budget = Decimal("0.00")
    expenditure = Decimal("50000.00")

    result = calculate_budget_utilization(budget, expenditure)

    assert result == Decimal("0.00")


# TEST 7: BUDGET REMAINING
def test_calculate_budget_remaining():

    budget = Decimal("1000000.00")
    expenditure = Decimal("700000.00")

    result = calculate_budget_remaining(budget, expenditure)

    assert result == Decimal("300000.00")


# TEST 8: BUDGET OVERRUN
def test_budget_overrun():

    budget = Decimal("1000000.00")
    expenditure = Decimal("1200000.00")

    result = calculate_budget_remaining(budget, expenditure)

    assert result == Decimal("-200000.00")