"""Tests for the TF-IDF job recommendation."""

from __future__ import annotations

import pandas as pd

from analysis.recommend import recommend_jobs
from cleaner.pipeline import clean_jobs
from datagen.sample_jobs import generate_sample_jobs


def test_recommend_returns_top_n_sorted() -> None:
    raw = generate_sample_jobs(count=120, seed=11)
    df, _ = clean_jobs(raw)
    profile = {
        "skills": "python 数据分析",
        "city": "上海",
        "education": "本科",
        "salary_max": 30.0,
    }
    result = recommend_jobs(df, profile, top_n=5)
    assert isinstance(result, pd.DataFrame)
    assert len(result) <= 5
    assert list(result["match_score"]) == sorted(result["match_score"], reverse=True)
    assert (result["city"] == "上海").all()


def test_recommend_hard_filters_apply() -> None:
    raw = generate_sample_jobs(count=80, seed=22)
    df, _ = clean_jobs(raw)
    profile = {"skills": "python", "city": "北京", "education": "硕士", "salary_max": 40.0}
    result = recommend_jobs(df, profile, top_n=10)
    if len(result) > 0:
        assert (result["city"] == "北京").all()
