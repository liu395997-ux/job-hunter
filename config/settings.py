"""Shared project paths and constants."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CLEANED_DIR = DATA_DIR / "cleaned"
SAMPLE_DIR = DATA_DIR / "sample"

SAMPLE_JOBS_CSV = SAMPLE_DIR / "sample_jobs.csv"
CLEANED_JOBS_CSV = CLEANED_DIR / "cleaned_jobs.csv"
QUALITY_REPORT_JSON = CLEANED_DIR / "quality_report.json"
SQLITE_DB_PATH = DATA_DIR / "jobs.db"
