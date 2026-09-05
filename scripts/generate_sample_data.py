"""Generate a deterministic sample job dataset as CSV."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import SAMPLE_JOBS_CSV  # noqa: E402
from datagen.sample_jobs import generate_sample_jobs  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=SAMPLE_JOBS_CSV, help="输出 CSV 路径")
    parser.add_argument("--count", type=int, default=320, help="生成行数")
    parser.add_argument("--seed", type=int, default=42, help="随机种子（保证可复现）")
    args = parser.parse_args()

    df = generate_sample_jobs(count=args.count, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(f"已生成 {len(df)} 条样例职位数据 -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
