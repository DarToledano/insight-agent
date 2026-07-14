"""Tests for ChartSelector rule-based chart selection."""

from app.services.chart_selector import ChartSelector


def test_empty_results_return_none():
    selector = ChartSelector()
    result = selector.select("Total revenue?", [], [])
    assert result.type == "none"


def test_single_numeric_value_returns_kpi():
    selector = ChartSelector()
    result = selector.select(
        "What is total revenue?",
        ["total_revenue"],
        [[125000.50]],
    )
    assert result.type == "kpi"
    assert result.y_key == "total_revenue"
    assert result.x_key == ""
    assert result.title == "Total Revenue"


def test_category_and_numeric_returns_bar():
    selector = ChartSelector()
    result = selector.select(
        "Which companies have the highest revenue?",
        ["name", "total_revenue"],
        [
            ["Zenith Consulting", 47940],
            ["SecureNet Corp", 28764],
            ["DataPulse Inc", 21000],
        ],
    )
    assert result.type == "bar"
    assert result.x_key == "name"
    assert result.y_key == "total_revenue"


def test_revenue_by_plan_returns_bar_when_heavily_skewed():
    selector = ChartSelector()
    result = selector.select(
        "Show total revenue by subscription plan",
        ["subscription_plan", "total_revenue"],
        [
            ["enterprise", 131036],
            ["pro", 4776],
            ["starter", 196],
        ],
    )
    assert result.type == "bar"
    assert result.x_key == "subscription_plan"
    assert result.y_key == "total_revenue"


def test_revenue_by_plan_returns_pie_when_balanced():
    selector = ChartSelector()
    result = selector.select(
        "Show total revenue by subscription plan",
        ["plan", "total_revenue"],
        [
            ["enterprise", 40000],
            ["pro", 35000],
            ["starter", 25000],
        ],
    )
    assert result.type == "pie"


def test_date_and_numeric_returns_line():
    selector = ChartSelector()
    result = selector.select(
        "Show daily revenue trend",
        ["paid_at", "daily_revenue"],
        [
            ["2024-01-01", 1000],
            ["2024-01-02", 1200],
            ["2024-01-03", 900],
            ["2024-01-04", 1500],
        ],
    )
    assert result.type == "line"
    assert result.x_key == "paid_at"
    assert result.y_key == "daily_revenue"


def test_too_many_rows_returns_none():
    selector = ChartSelector()
    rows = [[f"Company {index}", index * 100] for index in range(50)]
    result = selector.select(
        "List all companies",
        ["name", "total_revenue"],
        rows,
    )
    assert result.type == "none"


def test_non_numeric_results_return_none():
    selector = ChartSelector()
    result = selector.select(
        "List company names",
        ["name"],
        [["Zenith Consulting"], ["SecureNet Corp"]],
    )
    assert result.type == "none"
