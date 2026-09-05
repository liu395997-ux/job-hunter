"""SQLite and CSV helpers for cleaned job data."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from cleaner.skills import skills_string_to_list


def save_jobs_to_sqlite(df: pd.DataFrame, db_path: str | Path) -> None:
    """Replace the ``jobs`` table with ``df`` content."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = df.copy()
    if "skill_list" in payload.columns:
        payload["skill_list"] = payload["skill_list"].map(
            lambda items: ",".join(items) if isinstance(items, list) else ""
        )
    with sqlite3.connect(path) as conn:
        payload.to_sql("jobs", conn, if_exists="replace", index=False)


def load_jobs_from_sqlite(db_path: str | Path) -> pd.DataFrame:
    """Load the ``jobs`` table back into a DataFrame."""
    with sqlite3.connect(Path(db_path)) as conn:
        df = pd.read_sql_query("SELECT * FROM jobs", conn)
    if "skill_list" in df.columns:
        df["skill_list"] = df["skill_list"].map(skills_string_to_list)
    return df


def save_jobs_to_csv(df: pd.DataFrame, csv_path: str | Path) -> None:
    """Persist cleaned jobs as UTF-8 CSV (BOM so Excel renders Chinese)."""
    path = Path(csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def load_jobs_from_csv(csv_path: str | Path) -> pd.DataFrame:
    """Load cleaned jobs from CSV."""
    return pd.read_csv(Path(csv_path))
