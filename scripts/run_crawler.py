"""CLI: crawl a real recruitment site with graceful fallback to sample data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from spider.config import SITES  # noqa: E402
from spider.crawler import run_crawl  # noqa: E402
from spider.http_client import HttpClient  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", choices=sorted(SITES), default="zhaopin", help="目标站点")
    parser.add_argument(
        "--keyword",
        action="append",
        dest="keywords",
        help="搜索关键词，可多次传入（默认取站点配置）",
    )
    parser.add_argument("--cities", default=None, help="城市列表，逗号分隔（默认取站点配置）")
    parser.add_argument("--pages", type=int, default=None, help="每个关键词-城市抓取页数")
    parser.add_argument("--strategy", choices=["bfs", "dfs"], default="bfs", help="调度策略")
    parser.add_argument("--interval", type=float, default=None, help="请求间隔秒")
    parser.add_argument("--raw-dir", type=Path, default=None, help="原始数据目录")
    parser.add_argument("--output", type=Path, default=None, help="结构化 CSV 输出路径")
    return parser


def main(argv: list[str] | None = None, http_client: HttpClient | None = None) -> int:
    args = build_parser().parse_args(argv)
    site = SITES[args.site]

    keywords = args.keywords or list(site["default_keywords"])
    default_cities = ",".join(site["default_cities"])
    cities = [
        city.strip() for city in (args.cities or default_cities).split(",") if city.strip()
    ]
    pages = args.pages or int(site["default_pages"])
    raw_dir = args.raw_dir or PROJECT_ROOT / "data" / "raw"
    output = args.output or PROJECT_ROOT / "data" / "raw" / f"jobs_{args.site}.csv"

    client = http_client or HttpClient(
        user_agents=site["user_agents"],
        interval=args.interval if args.interval is not None else float(site["default_interval"]),
    )

    result = run_crawl(
        site=args.site,
        keywords=keywords,
        cities=cities,
        pages=pages,
        strategy=args.strategy,
        http_client=client,
        raw_dir=raw_dir,
        output_csv=output,
        site_config=site,
    )

    if result.job_count:
        print(
            f"抓取完成：{result.job_count} 条职位 -> {result.output_csv}"
            f"（原始文件 {len(result.raw_files)} 个）"
        )
        for error in result.errors[:5]:
            print(f"  警告：{error}", file=sys.stderr)
        return 0

    sample_error = result.errors[0] if result.errors else "未知错误"
    print(
        f"抓取失败：{len(result.errors)}/{result.task_count} 个任务未成功"
        f"（示例：{sample_error}）。\n"
        "真实站点不可达或反爬，请使用样例数据：python scripts/run_pipeline.py",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
