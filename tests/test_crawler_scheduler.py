"""Tests for the BFS/DFS task scheduler."""

from __future__ import annotations

from spider.config import build_url
from spider.scheduler import build_tasks


def test_bfs_and_dfs_cover_same_tasks() -> None:
    keywords = ["数据分析", "Python"]
    cities = ["北京", "上海"]
    pages = 2
    bfs = build_tasks("zhaopin", keywords, cities, pages, strategy="bfs")
    dfs = build_tasks("zhaopin", keywords, cities, pages, strategy="dfs")
    assert {task.url for task in bfs} == {task.url for task in dfs}
    assert len(bfs) == len(dfs) == len(keywords) * len(cities) * pages


def test_bfs_and_dfs_order_differ() -> None:
    keywords = ["数据分析", "Python"]
    cities = ["北京", "上海"]
    bfs = build_tasks("zhaopin", keywords, cities, 2, strategy="bfs")
    dfs = build_tasks("zhaopin", keywords, cities, 2, strategy="dfs")
    assert [task.url for task in bfs] != [task.url for task in dfs]


def test_bfs_orders_by_page_first() -> None:
    tasks = build_tasks("zhaopin", ["k1"], ["北京", "上海"], 2, strategy="bfs")
    page_sequence = [task.page for task in tasks]
    assert page_sequence == [1, 1, 2, 2]


def test_dfs_crawls_all_pages_of_first_pair() -> None:
    tasks = build_tasks("zhaopin", ["k1"], ["北京", "上海"], 2, strategy="dfs")
    first_pair_pages = [task.page for task in tasks[:2]]
    assert first_pair_pages == [1, 2]


def test_build_url_contains_query_parameters() -> None:
    url = build_url("zhaopin", "数据分析", "北京", 2)
    assert "kw=" in url and "cityId=" in url and "p=2" in url and "pageSize=" in url
