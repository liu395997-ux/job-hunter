"""Shared text tokenization for Chinese + English job text."""

from __future__ import annotations

import re

import jieba

_TOKEN_RE = re.compile(r"^[a-z0-9_+#.\-]+$|^[\u4e00-\u9fff]+$")


def tokenize(text: str | None) -> list[str]:
    """Split mixed Chinese/English text into meaningful tokens via jieba."""
    if not text:
        return []
    tokens: list[str] = []
    for word in jieba.lcut(str(text).lower()):
        if _TOKEN_RE.fullmatch(word):
            tokens.append(word)
    return tokens
