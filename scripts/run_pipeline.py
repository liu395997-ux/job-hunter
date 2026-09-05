"""One-command pipeline: sample data -> clean -> SQLite -> analysis summary."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis.cluster import cluster_jobs  # noqa: E402
from analysis.salary_predict import train_salary_model  # noqa: E402
from cleaner.pipeline import clean_jobs, write_quality_report  # noqa: E402
from config.settings import (  # noqa: E402
    CLEANED_JOBS_CSV,
    DATA_DIR,
    QUALITY_REPORT_JSON,
    SAMPLE_JOBS_CSV,
    SQLITE_DB_PATH,
)
from datagen.sample_jobs import generate_sample_jobs  # noqa: E402
from storage.db import load_jobs_from_sqlite, save_jobs_to_csv, save_jobs_to_sqlite  # noqa: E402


def _load_or_generate_raw(input_path: Path) -> object:
    import pandas as pd

    if input_path.exists():
        return pd.read_csv(input_path)
    print(f"未找到 {input_path}，自动生成样例数据")
    df = generate_sample_jobs()
    input_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(input_path, index=False, encoding="utf-8-sig")
    return df


def _default_input_path() -> Path:
    crawled = DATA_DIR / "raw" / "jobs_zhaopin.csv"
    if crawled.exists():
        return crawled
    return SAMPLE_JOBS_CSV


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=_default_input_path(),
        help="原始数据 CSV（默认优先真实爬取结果）",
    )
    parser.add_argument("--cleaned", type=Path, default=CLEANED_JOBS_CSV, help="清洗后 CSV")
    parser.add_argument("--db", type=Path, default=SQLITE_DB_PATH, help="SQLite 路径")
    parser.add_argument("--report", type=Path, default=QUALITY_REPORT_JSON, help="质量报告 JSON")
    args = parser.parse_args()

    raw = _load_or_generate_raw(args.input)
    cleaned, report = clean_jobs(raw)
    save_jobs_to_csv(cleaned, args.cleaned)
    save_jobs_to_sqlite(cleaned, args.db)
    write_quality_report(report, args.report)

    loaded = load_jobs_from_sqlite(args.db)
    _, metrics = train_salary_model(loaded)
    clustered = cluster_jobs(loaded, k=4)

    print(
        f"原始行数：{report['rows_before']} | 清洗后：{report['rows_after']} "
        f"| 去重：{report['duplicates_removed']}"
    )
    print(f"薪资预测 MAE={metrics['mae']:.2f}K R2={metrics['r2']:.3f}")
    print(
        f"聚类轮廓系数={clustered.attrs['silhouette']:.3f}"
        f"（簇数 {clustered.attrs['cluster_count']}）"
    )
    print(f"已输出：{args.cleaned} / {args.report} / {args.db}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
