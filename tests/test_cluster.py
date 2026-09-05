"""Tests for the KMeans job clustering."""

from __future__ import annotations

from analysis.cluster import cluster_jobs, cluster_profiles
from cleaner.pipeline import clean_jobs
from datagen.sample_jobs import generate_sample_jobs


def test_cluster_returns_labels_and_silhouette() -> None:
    raw = generate_sample_jobs(count=100, seed=9)
    df, _ = clean_jobs(raw)
    result = cluster_jobs(df, k=4)
    assert "cluster" in result.columns
    assert -1.0 <= result.attrs["silhouette"] <= 1.0


def test_cluster_profiles_are_interpretable() -> None:
    raw = generate_sample_jobs(count=80, seed=13)
    df, _ = clean_jobs(raw)
    result = cluster_jobs(df, k=3)
    profiles = cluster_profiles(result)
    assert len(profiles) == 3
    for _, row in profiles.iterrows():
        assert row["top_skills"]
