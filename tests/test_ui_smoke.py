"""Streamlit AppTest smoke tests: every page renders without exceptions."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

import pytest
from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PAGES = [PROJECT_ROOT / path for path in (
    "streamlit_app.py",
    "app_pages/overview.py",
    "app_pages/salary.py",
    "app_pages/skills.py",
    "app_pages/match.py",
)]


@pytest.mark.parametrize("page_file", PAGES)
def test_page_renders_without_exception(page_file: str) -> None:
    app = AppTest.from_file(page_file, default_timeout=180)
    app.run()
    assert not app.exception, f"{page_file} raised {app.exception}"


def test_match_form_returns_recommendations() -> None:
    app = AppTest.from_file(PROJECT_ROOT / "app_pages/match.py", default_timeout=180)
    app.run()
    app.text_input[0].set_value("python, 数据分析, sql")
    app.button[0].click().run()
    assert not app.exception
    assert len(app.dataframe) >= 1
