"""Tests for SQLite/CSV storage helpers."""

from __future__ import annotations

import pandas as pd

from cleaner.pipeline import clean_jobs
from datagen.sample_jobs import generate_sample_jobs
from storage.db import load_jobs_from_sqlite, save_jobs_to_sqlite


def test_sqlite_roundtrip(tmp_path) -> None:
    raw = generate_sample_jobs(count=60, seed=2)
    df, _ = clean_jobs(raw)
    db_path = tmp_path / "jobs.db"
    save_jobs_to_sqlite(df, db_path)
    loaded = load_jobs_from_sqlite(db_path)
    assert len(loaded) == len(df)
    assert "salary_avg" in loaded.columns
    assert isinstance(loaded, pd.DataFrame)
