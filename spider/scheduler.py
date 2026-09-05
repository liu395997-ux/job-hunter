"""BFS/DFS task scheduling for crawl jobs."""

from __future__ import annotations

from dataclasses import dataclass

from spider.config import build_url


@dataclass(frozen=True)
class Task:
    """A single crawl unit: one keyword-city-page combination."""

    site: str
    keyword: str
    city: str
    page: int
    url: str


def build_tasks(
    site: str,
    keywords: list[str],
    cities: list[str],
    pages: int,
    strategy: str = "bfs",
) -> list[Task]:
    """Build crawl tasks; bfs covers pages breadth-first, dfs depth-first."""
    tasks = [
        Task(site, keyword, city, page, build_url(site, keyword, city, page))
        for keyword in keywords
        for city in cities
        for page in range(1, pages + 1)
    ]
    if strategy == "bfs":
        tasks.sort(key=lambda task: (task.page, task.keyword, task.city))
    else:
        tasks.sort(key=lambda task: (task.keyword, task.city, task.page))
    return tasks
