"""Tests for the cleaning pipeline."""

from __future__ import annotations

import pandas as pd

from cleaner.pipeline import (
    clean_jobs,
    deduplicate_jobs,
    normalize_company_size,
    normalize_education,
    normalize_experience,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "title": "数据分析师",
                "company": "甲公司",
                "city": "上海",
                "salary_text": "16-26K",
                "education": "本科",
                "experience": "1-3年",
                "company_size": "150-500人",
                "company_type": "民营",
                "skills": "python, sql",
                "description": "负责数据分析工作",
                "publish_date": "2026-08-01",
                "link": "https://job.example.com/1",
            },
            {
                "title": "数据分析师",
                "company": "甲公司",
                "city": "上海",
                "salary_text": "15-25K",
                "education": "本科及以上",
                "experience": "经验不限",
                "company_size": "150-500人",
                "company_type": "民营",
                "skills": "python",
                "description": "负责数据分析工作",
                "publish_date": "2026-08-02",
                "link": "https://job.example.com/2",
            },
            {
                "title": "算法工程师",
                "company": "乙公司",
                "city": "北京",
                "salary_text": "面议",
                "education": "硕士",
                "experience": "3-5年",
                "company_size": "少于50人",
                "company_type": "合资",
                "skills": "机器学习, python",
                "description": "负责推荐算法研发",
                "publish_date": "2026-08-03",
                "link": "https://job.example.com/3",
            },
        ]
    )


def test_normalize_education_maps_categories() -> None:
    values = normalize_education(pd.Series(["本科", "本科及以上", "硕士", "学历不限", "大专"]))
    assert set(values) == {"本科", "硕士", "大专", "不限"}


def test_normalize_experience_maps_categories() -> None:
    values = normalize_experience(pd.Series(["经验不限", "在校/应届", "1-3年", "5-10年"]))
    assert set(values) == {"经验不限", "在校/应届", "1-3年", "5-10年"}


def test_normalize_company_size_maps_categories() -> None:
    values = normalize_company_size(pd.Series(["少于50人", "50-150人", "2000人以上"]))
    assert set(values) == {"少于50人", "50-150人", "2000人以上"}


def test_deduplicate_removes_exact_duplicates() -> None:
    df = _sample_df()
    duplicated = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    result = deduplicate_jobs(duplicated)
    assert len(result) == len(df)


def test_clean_jobs_adds_salary_columns_and_report() -> None:
    cleaned, report = clean_jobs(_sample_df())
    for col in ("salary_min", "salary_max", "salary_avg"):
        assert col in cleaned.columns
    assert report["rows_before"] == 3
    assert report["rows_after"] <= 3
    assert "missing_rate" in report
