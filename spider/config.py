"""Site configurations and URL builders for the crawler."""

from __future__ import annotations

from urllib.parse import urlencode

DEFAULT_USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0"
    ),
]

ZHAOPIN = {
    "name": "zhaopin",
    "api_url": "https://fe-api.zhaopin.com/c/i/sou",
    "city_ids": {
        "北京": 530,
        "上海": 538,
        "广州": 763,
        "深圳": 765,
        "杭州": 653,
        "成都": 801,
        "武汉": 736,
        "南京": 635,
    },
    "default_keywords": ["数据分析", "Python开发", "机器学习"],
    "default_cities": ["北京", "上海", "深圳", "杭州"],
    "default_pages": 3,
    "default_interval": 1.2,
    "page_size": 90,
    "user_agents": DEFAULT_USER_AGENTS,
}

SITES = {"zhaopin": ZHAOPIN}


def build_url(site_name: str, keyword: str, city: str, page: int) -> str:
    """Build the search API URL for a keyword/city/page combo."""
    site = SITES[site_name]
    params = {
        "kw": keyword,
        "cityId": site["city_ids"][city],
        "p": page,
        "pageSize": site["page_size"],
    }
    return f"{site['api_url']}?{urlencode(params)}"
