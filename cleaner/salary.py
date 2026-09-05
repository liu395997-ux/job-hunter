"""Salary text parsing and normalization."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SalaryRange:
    """Parsed monthly salary in K (thousand CNY)."""

    min_salary: float | None
    max_salary: float | None
    avg_salary: float | None


_K_RANGE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*[-~]\s*(\d+(?:\.\d+)?)\s*K", re.IGNORECASE)
_MIXED_RANGE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*千\s*[-~]\s*(\d+(?:\.\d+)?)\s*万/月")
_WAN_RANGE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*[-~]\s*(\d+(?:\.\d+)?)\s*万/月")


def parse_salary(text: str | None) -> SalaryRange | None:
    """Parse a Chinese salary string into a monthly K range, or None."""
    if not text or "面议" in text:
        return None

    match = _K_RANGE_RE.search(text)
    if match:
        low, high = float(match.group(1)), float(match.group(2))
        return SalaryRange(low, high, round((low + high) / 2, 2))

    match = _MIXED_RANGE_RE.search(text)
    if match:
        low = float(match.group(1))  # 8千 -> 8K
        high = float(match.group(2)) * 10  # 1.2万 -> 12K
        return SalaryRange(low, high, round((low + high) / 2, 2))

    match = _WAN_RANGE_RE.search(text)
    if match:
        low = float(match.group(1)) * 10
        high = float(match.group(2)) * 10
        return SalaryRange(low, high, round((low + high) / 2, 2))

    return None
