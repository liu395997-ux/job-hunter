"""Rate-limited, retrying HTTP client with a rotating UA pool."""

from __future__ import annotations

import random
import time
from collections.abc import Callable

import requests

from spider.config import DEFAULT_USER_AGENTS

Fetcher = Callable[[str, dict[str, str], float], tuple[int, str]]


class FetchError(RuntimeError):
    """Raised when every retry attempt fails for a URL."""


class HttpClient:
    """Fetch text with UA rotation, rate limiting and exponential backoff."""

    def __init__(
        self,
        user_agents: list[str] | None = None,
        interval: float = 1.0,
        timeout: float = 10.0,
        retries: int = 3,
        backoff_base: float = 1.0,
        seed: int = 42,
        fetcher: Fetcher | None = None,
    ) -> None:
        self._user_agents = list(user_agents or DEFAULT_USER_AGENTS)
        self._interval = max(0.0, interval)
        self._timeout = timeout
        self._retries = max(1, retries)
        self._backoff_base = backoff_base
        self._ua_index = 0
        self._last_request_at = 0.0
        self._fetcher = fetcher or self._default_fetcher
        random.seed(seed)

    def _default_fetcher(
        self, url: str, headers: dict[str, str], timeout: float
    ) -> tuple[int, str]:
        response = requests.get(url, headers=headers, timeout=timeout)
        return response.status_code, response.text

    def _next_user_agent(self) -> str:
        agent = self._user_agents[self._ua_index % len(self._user_agents)]
        self._ua_index += 1
        return agent

    def _respect_rate_limit(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self._interval:
            time.sleep(self._interval - elapsed)

    def fetch(self, url: str) -> str:
        """Fetch a URL, retrying transient failures; raise FetchError on failure."""
        last_error: Exception | None = None
        for attempt in range(self._retries):
            self._respect_rate_limit()
            headers = {
                "User-Agent": self._next_user_agent(),
                "Referer": "https://www.zhaopin.com/",
                "Accept": "application/json, text/plain, */*",
            }
            try:
                status, text = self._fetcher(url, headers, self._timeout)
            except Exception as exc:  # network-level failures
                last_error = exc
            else:
                if status < 400:
                    self._last_request_at = time.monotonic()
                    return text
                last_error = FetchError(f"HTTP {status}")
            if attempt + 1 < self._retries and self._backoff_base > 0:
                time.sleep(self._backoff_base * (2**attempt))
        raise FetchError(f"请求失败（{self._retries} 次重试后）：{url}；原因：{last_error}")
