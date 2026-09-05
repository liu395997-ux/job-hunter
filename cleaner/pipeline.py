"""End-to-end cleaning pipeline: salary, dedup, normalization, report."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd

from cleaner.salary import parse_salary
from cleaner.skills import skills_string_to_list

EDUCATION_MAP = {
    "本科及以上": "本科",
    "硕士及以上": "硕士",
    "博士及以上": "博士",
    "大专及以上": "大专",
    "学历不限": "不限",
    "不限": "不限",
}

EXPERIENCE_MAP = {
    "1-3年经验": "1-3年",
    "3-5年经验": "3-5年",
    "5-10年经验": "5-10年",
    "10年以上经验": "10年以上",
    "在校生/应届生": "在校/应届",
}

COMPANY_SIZE_MAP = {
    "少于50人": "少于50人",
    "50-150人": "50-150人",
    "150-500人": "150-500人",
    "500-2000人": "500-2000人",
    "2000人以上": "2000人以上",
}


def normalize_education(series: pd.Series) -> pd.Series:
    """Map education variants to a small set of categories."""
    return series.map(lambda value: EDUCATION_MAP.get(str(value).strip(), str(value).strip()))


def normalize_experience(series: pd.Series) -> pd.Series:
    """Map experience variants to a small set of categories."""
    return series.map(lambda value: EXPERIENCE_MAP.get(str(value).strip(), str(value).strip()))


def normalize_company_size(series: pd.Series) -> pd.Series:
    """Normalize company-size strings; unknown values pass through."""
    return series.map(lambda value: COMPANY_SIZE_MAP.get(str(value).strip(), str(value).strip()))


def deduplicate_jobs(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows sharing title, company, city and raw salary text."""
    keys = ["title", "company", "city", "salary_text"]
    return df.drop_duplicates(subset=keys, keep="first").reset_index(drop=True)


def clean_jobs(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Clean raw job rows; return (cleaned_df, quality_report)."""
    work = df.copy()
    rows_before = len(work)

    parsed = work["salary_text"].map(parse_salary)
    work["salary_min"] = parsed.map(lambda item: item.min_salary if item else None)
    work["salary_max"] = parsed.map(lambda item: item.max_salary if item else None)
    work["salary_avg"] = parsed.map(lambda item: item.avg_salary if item else None)

    work["education"] = normalize_education(work["education"])
    work["experience"] = normalize_experience(work["experience"])
    work["company_size"] = normalize_company_size(work["company_size"])

    work["skill_list"] = work["skills"].map(skills_string_to_list)
    work["skill_count"] = work["skill_list"].map(len)

    cleaned = deduplicate_jobs(work)
    missing_rate = {
        column: round(float(cleaned[column].isna().mean()), 4)
        for column in ("salary_min", "salary_avg", "description", "skills")
    }
    report: dict[str, Any] = {
        "rows_before": rows_before,
        "rows_after": len(cleaned),
        "duplicates_removed": rows_before - len(cleaned),
        "missing_rate": missing_rate,
        "education_distribution": cleaned["education"].value_counts().to_dict(),
    }
    return cleaned, report


def write_quality_report(report: dict[str, Any], output_path) -> None:
    """Persist a quality report as JSON for auditability."""
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
