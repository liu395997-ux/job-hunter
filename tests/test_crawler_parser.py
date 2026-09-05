"""Tests for the Zhaopin JSON/HTML parsers."""

from __future__ import annotations

from spider.parsers import parse_zhaopin_html, parse_zhaopin_json


def _sample_payload() -> dict:
    return {
        "data": {
            "results": [
                {
                    "jobName": "数据分析师",
                    "city": {"display": "北京"},
                    "eduLevel": {"name": "本科"},
                    "workingExp": {"name": "1-3年"},
                    "company": {
                        "name": "示例科技",
                        "size": {"name": "150-500人"},
                        "type": {"name": "民营"},
                    },
                    "salary": "15-25K·14薪",
                    "jobWelfare": ["五险一金", "年终奖"],
                    "jobDesc": "负责数据分析工作，要求掌握 python 与 sql",
                    "publishTime": "2026-08-29T10:00:00+08:00",
                    "positionURL": "https://jobs.zhaopin.com/123456.htm",
                }
            ]
        }
    }


def test_parse_zhaopin_json_extracts_standard_fields() -> None:
    jobs = parse_zhaopin_json(_sample_payload())
    assert len(jobs) == 1
    job = jobs[0]
    assert job["title"] == "数据分析师"
    assert job["city"] == "北京"
    assert job["education"] == "本科"
    assert job["experience"] == "1-3年"
    assert job["company"] == "示例科技"
    assert job["company_size"] == "150-500人"
    assert job["company_type"] == "民营"
    assert job["salary_text"] == "15-25K·14薪"
    assert "python" in job["skills"]
    assert job["publish_date"] == "2026-08-29"
    assert job["link"] == "https://jobs.zhaopin.com/123456.htm"


def test_parse_zhaopin_json_tolerates_missing_fields() -> None:
    payload = {"data": {"results": [{"jobName": "仅职位"}]}}
    jobs = parse_zhaopin_json(payload)
    assert len(jobs) == 1
    assert jobs[0]["title"] == "仅职位"
    assert jobs[0]["city"] == ""
    assert jobs[0]["salary_text"] == ""
    assert jobs[0]["link"] == ""


def test_parse_zhaopin_json_empty_payload() -> None:
    assert parse_zhaopin_json({}) == []
    assert parse_zhaopin_json({"data": {"results": []}}) == []


def test_parse_zhaopin_html_finds_job_links() -> None:
    html = (
        '<html><body><a href="https://jobs.zhaopin.com/1.htm">数据分析师</a>'
        '<a href="https://jobs.zhaopin.com/2.htm">算法工程师</a></body></html>'
    )
    jobs = parse_zhaopin_html(html)
    assert len(jobs) == 2
    assert jobs[0]["link"] == "https://jobs.zhaopin.com/1.htm"
    assert jobs[0]["title"] == "数据分析师"
