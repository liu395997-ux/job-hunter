"""Tests for salary text parsing."""

from __future__ import annotations

from cleaner.salary import SalaryRange, parse_salary


def test_parse_k_range() -> None:
    result = parse_salary("15-25K")
    assert result == SalaryRange(min_salary=15.0, max_salary=25.0, avg_salary=20.0)


def test_parse_k_range_with_bonus_months() -> None:
    result = parse_salary("15-25K·14薪")
    assert result == SalaryRange(min_salary=15.0, max_salary=25.0, avg_salary=20.0)


def test_parse_wan_per_month() -> None:
    result = parse_salary("1-2万/月")
    assert result == SalaryRange(min_salary=10.0, max_salary=20.0, avg_salary=15.0)


def test_parse_qian_to_wan() -> None:
    result = parse_salary("8千-1.2万/月")
    assert result == SalaryRange(min_salary=8.0, max_salary=12.0, avg_salary=10.0)


def test_parse_salary_negotiable_returns_none() -> None:
    assert parse_salary("面议") is None
    assert parse_salary("薪资面议") is None


def test_parse_unknown_format_returns_none() -> None:
    assert parse_salary("") is None
    assert parse_salary("200-300元/天") is None
    assert parse_salary("随便写点啥") is None
