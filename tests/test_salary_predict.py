"""Tests for the salary prediction model."""

from __future__ import annotations

import math

from analysis.salary_predict import predict_salary, train_salary_model
from cleaner.pipeline import clean_jobs
from datagen.sample_jobs import generate_sample_jobs


def test_train_and_predict_produce_finite_metrics() -> None:
    raw = generate_sample_jobs(count=200, seed=5)
    df, _ = clean_jobs(raw)
    model, metrics = train_salary_model(df)
    assert math.isfinite(metrics["mae"])
    assert math.isfinite(metrics["r2"])
    assert "feature_importance" in metrics
    sample = df.dropna(subset=["salary_avg"]).iloc[0]
    prediction = predict_salary(model, sample)
    assert math.isfinite(prediction)
    assert prediction > 0
