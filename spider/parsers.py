"""Parsers for the Zhaopin JSON API and an HTML fallback."""

from __future__ import annotations

from bs4 import BeautifulSoup

from cleaner.skills import extract_skills

JOB_FIELDS = [
    "title",
    "city",
    "education",
    "experience",
    "company",
    "company_size",
    "company_type",
    "salary_text",
    "skills",
    "description",
    "publish_date",
    "link",
]


def _get(item: object, *keys: str) -> object:
    """Safely traverse nested dicts, returning None for missing paths."""
    value: object = item
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def parse_zhaopin_json(payload: dict) -> list[dict[str, str]]:
    """Parse the fe-api.zhaopin.com search response into job rows."""
    results = (_get(payload, "data", "results") or []) if isinstance(payload, dict) else []
    jobs: list[dict[str, str]] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        description = str(_get(item, "jobDesc") or "")
        welfare = _get(item, "jobWelfare") or []
        welfare_text = " ".join(str(tag) for tag in welfare) if isinstance(welfare, list) else ""
        skills = extract_skills(f"{description} {welfare_text}")
        jobs.append(
            {
                "title": str(_get(item, "jobName") or "").strip(),
                "city": str(_get(item, "city", "display") or "").strip(),
                "education": str(_get(item, "eduLevel", "name") or "").strip(),
                "experience": str(_get(item, "workingExp", "name") or "").strip(),
                "company": str(_get(item, "company", "name") or "").strip(),
                "company_size": str(_get(item, "company", "size", "name") or "").strip(),
                "company_type": str(_get(item, "company", "type", "name") or "").strip(),
                "salary_text": str(_get(item, "salary") or "").strip(),
                "skills": ", ".join(skills),
                "description": description,
                "publish_date": str(_get(item, "publishTime") or "")[:10],
                "link": str(_get(item, "positionURL") or "").strip(),
            }
        )
    return jobs


def parse_zhaopin_html(html: str) -> list[dict[str, str]]:
    """Fallback: extract job title/link pairs from HTML job list pages."""
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict[str, str]] = []
    for anchor in soup.find_all("a", href=True):
        href = str(anchor["href"])
        title = anchor.get_text(strip=True)
        if "jobs.zhaopin.com" in href and title:
            jobs.append({"title": title, "link": href})
    return jobs
