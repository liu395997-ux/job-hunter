"""Cached data and model loading for the Streamlit app."""

from __future__ import annotations

import os

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

import pandas as pd
import streamlit as st

from analysis.salary_predict import train_salary_model
from cleaner.pipeline import clean_jobs
from config.settings import CLEANED_JOBS_CSV, SQLITE_DB_PATH
from datagen.sample_jobs import generate_sample_jobs
from storage.db import load_jobs_from_csv, load_jobs_from_sqlite


@st.cache_data(ttl="10m", max_entries=4, show_spinner="加载职位数据…")
def load_cleaned_data() -> pd.DataFrame:
    """Load cleaned jobs, preferring SQLite, then CSV, then on-the-fly sample data."""
    if SQLITE_DB_PATH.exists():
        return load_jobs_from_sqlite(SQLITE_DB_PATH)
    if CLEANED_JOBS_CSV.exists():
        return load_jobs_from_csv(CLEANED_JOBS_CSV)
    raw = generate_sample_jobs()
    cleaned, _ = clean_jobs(raw)
    return cleaned


@st.cache_resource(show_spinner="训练薪资预测模型…")
def load_salary_pipeline():
    """Train and cache the RandomForest salary pipeline."""
    df = load_cleaned_data()
    pipeline, _ = train_salary_model(df)
    return pipeline


@st.cache_data(ttl="10m", show_spinner="计算薪资模型指标…")
def load_salary_metrics() -> dict:
    """Train once and return model metrics for the salary page."""
    df = load_cleaned_data()
    _, metrics = train_salary_model(df)
    return metrics
