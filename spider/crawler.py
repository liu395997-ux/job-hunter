"""Crawl orchestration: fetch tasks, parse results, persist raw files and CSV."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from spider.config import SITES
from spider.parsers import JOB_FIELDS, parse_zhaopin_html, parse_zhaopin_json
from spider.scheduler import build_tasks


@dataclass
class CrawlResult:
    """Outcome of a crawl run."""

    job_count: int
    task_count: int
    raw_files: list[Path] = field(default_factory=list)
    output_csv: Path | None = None
    errors: list[str] = field(default_factory=list)


def run_crawl(
    site: str,
    keywords: list[str],
    cities: list[str],
    pages: int,
    strategy: str,
    http_client,
    raw_dir: str | Path,
    output_csv: str | Path,
    site_config: dict | None = None,
) -> CrawlResult:
    """Fetch all tasks, persist raw payloads and a structured CSV of jobs."""
    site_config = site_config or SITES[site]
    tasks = build_tasks(site, keywords, cities, pages, strategy)
    raw_dir_path = Path(raw_dir)
    raw_dir_path.mkdir(parents=True, exist_ok=True)

    jobs: list[dict[str, str]] = []
    raw_files: list[Path] = []
    errors: list[str] = []

    for index, task in enumerate(tasks, start=1):
        try:
            text = http_client.fetch(task.url)
        except Exception as exc:
            errors.append(f"{task.url}: {exc}")
            continue

        raw_path = raw_dir_path / f"{site}_{index:03d}_{task.city}_{task.keyword}_{task.page}.json"
        raw_path.write_text(text, encoding="utf-8")
        raw_files.append(raw_path)

        try:
            payload = json.loads(text)
            jobs.extend(parse_zhaopin_json(payload))
        except json.JSONDecodeError:
            jobs.extend(parse_zhaopin_html(text))

    result = CrawlResult(job_count=len(jobs), task_count=len(tasks), errors=errors)
    result.raw_files = raw_files

    if jobs:
        frame = pd.DataFrame(jobs, columns=JOB_FIELDS)
        output = Path(output_csv)
        output.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(output, index=False, encoding="utf-8-sig")
        result.output_csv = output
    return result
