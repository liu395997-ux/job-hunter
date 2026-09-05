"""Tests for the deterministic sample job data generator."""

from __future__ import annotations

import pandas as pd

from datagen.sample_jobs import SAMPLE_FIELDS, generate_sample_jobs


def test_generates_at_least_300_rows() -> None:
    df = generate_sample_jobs(count=320, seed=42)
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 300


def test_contains_required_fields() -> None:
    df = generate_sample_jobs(count=50, seed=1)
    for field in SAMPLE_FIELDS:
        assert field in df.columns, f"missing field {field}"


def test_is_deterministic() -> None:
    first = generate_sample_jobs(count=100, seed=7)
    second = generate_sample_jobs(count=100, seed=7)
    pd.testing.assert_frame_equal(first, second)


def test_rows_are_nonempty() -> None:
    df = generate_sample_jobs(count=60, seed=3)
    assert (df["title"].str.len() > 0).all()
    assert (df["company"].str.len() > 0).all()
    assert (df["description"].str.len() > 20).all()
