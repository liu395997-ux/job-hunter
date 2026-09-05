"""CLI tests for scripts/run_crawler.py with an injected fake fetcher."""

from __future__ import annotations

import json

from scripts import run_crawler
from spider.http_client import HttpClient


def _sample_payload() -> dict:
    return {
        "data": {
            "results": [
                {
                    "jobName": "数据分析师",
                    "city": {"display": "北京"},
                    "eduLevel": {"name": "本科"},
                    "workingExp": {"name": "1-3年"},
                    "company": {"name": "示例科技", "size": {"name": "150-500人"}},
                    "salary": "15-25K",
                    "jobWelfare": ["python"],
                    "jobDesc": "数据分析",
                    "publishTime": "2026-08-29T10:00:00+08:00",
                    "positionURL": "https://jobs.zhaopin.com/1.htm",
                }
            ]
        }
    }


def _fake_http_client(ok: bool = True) -> HttpClient:
    def requester(url, headers, timeout):
        if not ok:
            return 500, "err"
        return 200, json.dumps(_sample_payload(), ensure_ascii=False)

    return HttpClient(interval=0.0, retries=1, backoff_base=0.0, fetcher=requester)


def test_run_crawler_writes_csv(tmp_path) -> None:
    exit_code = run_crawler.main(
        [
            "--site",
            "zhaopin",
            "--keyword",
            "数据分析",
            "--cities",
            "北京",
            "--pages",
            "1",
            "--interval",
            "0",
            "--raw-dir",
            str(tmp_path / "raw"),
            "--output",
            str(tmp_path / "jobs.csv"),
        ],
        http_client=_fake_http_client(ok=True),
    )
    assert exit_code == 0
    csv_path = tmp_path / "jobs.csv"
    assert csv_path.exists()
    content = csv_path.read_text(encoding="utf-8-sig")
    assert "数据分析师" in content
    assert "salary_text" in content


def test_run_crawler_all_fail_returns_nonzero(tmp_path, capsys) -> None:
    exit_code = run_crawler.main(
        [
            "--site",
            "zhaopin",
            "--keyword",
            "数据分析",
            "--cities",
            "北京",
            "--pages",
            "1",
            "--interval",
            "0",
            "--raw-dir",
            str(tmp_path / "raw"),
            "--output",
            str(tmp_path / "jobs.csv"),
        ],
        http_client=_fake_http_client(ok=False),
    )
    assert exit_code != 0
    captured = capsys.readouterr()
    assert "样例数据" in captured.err
