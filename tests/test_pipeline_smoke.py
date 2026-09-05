"""End-to-end smoke test: generate -> clean -> store -> analyze."""

from __future__ import annotations

import math

from analysis.cluster import cluster_jobs
from analysis.salary_predict import train_salary_model
from cleaner.pipeline import clean_jobs
from datagen.sample_jobs import generate_sample_jobs
from storage.db import load_jobs_from_sqlite, save_jobs_to_sqlite


def test_full_pipeline_smoke(tmp_path) -> None:
    raw = generate_sample_jobs(count=150, seed=17)
    df, report = clean_jobs(raw)
    assert report["rows_after"] >= 100
    db_path = tmp_path / "jobs.db"
    save_jobs_to_sqlite(df, db_path)
    loaded = load_jobs_from_sqlite(db_path)
    assert len(loaded) == len(df)
    _, metrics = train_salary_model(loaded)
    assert math.isfinite(metrics["mae"])
    clustered = cluster_jobs(loaded, k=3)
    assert clustered["cluster"].nunique() == 3
