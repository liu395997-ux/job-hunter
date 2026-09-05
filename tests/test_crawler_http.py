"""Tests for the retrying, rate-limited HTTP client."""

from __future__ import annotations

import time

import pytest

from spider.http_client import FetchError, HttpClient


def _fake_fetcher(status=200, text="ok"):
    def fetcher(url, headers, timeout):
        return status, text

    return fetcher


def test_fetch_success_returns_text() -> None:
    client = HttpClient(interval=0.0, retries=2, backoff_base=0.0, fetcher=_fake_fetcher())
    result = client.fetch("https://example.com")
    assert result == "ok"


def test_retries_on_server_error_then_succeeds() -> None:
    calls: list[int] = []

    def flaky(url, headers, timeout):
        calls.append(1)
        if len(calls) < 3:
            return 500, "err"
        return 200, "recovered"

    client = HttpClient(interval=0.0, retries=3, backoff_base=0.0, fetcher=flaky)
    assert client.fetch("https://example.com") == "recovered"
    assert len(calls) == 3


def test_retries_exhausted_raises_fetch_error() -> None:
    client = HttpClient(
        interval=0.0, retries=2, backoff_base=0.0, fetcher=_fake_fetcher(500, "err")
    )
    with pytest.raises(FetchError, match="https://example.com"):
        client.fetch("https://example.com")


def test_rate_limit_interval_between_requests() -> None:
    client = HttpClient(interval=0.15, retries=1, backoff_base=0.0, fetcher=_fake_fetcher())
    started = time.monotonic()
    client.fetch("https://example.com/1")
    client.fetch("https://example.com/2")
    elapsed = time.monotonic() - started
    assert elapsed >= 0.14


def test_user_agent_cycles_through_pool() -> None:
    seen: list[str] = []

    def record(url, headers, timeout):
        seen.append(headers["User-Agent"])
        return 200, "ok"

    client = HttpClient(
        user_agents=["UA-1", "UA-2", "UA-3"],
        interval=0.0,
        retries=1,
        backoff_base=0.0,
        fetcher=record,
    )
    for index in range(3):
        client.fetch(f"https://example.com/{index}")
    assert len(set(seen)) == 3
    assert seen[0] != seen[1]
