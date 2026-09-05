"""Skill frequency and co-occurrence analysis for the skills page."""

from __future__ import annotations

from collections import Counter
from itertools import combinations

import pandas as pd

from cleaner.skills import skills_string_to_list


def top_skills(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Return the most frequent skills across all jobs."""
    counter: Counter[str] = Counter()
    for skills in df["skills"].dropna():
        counter.update(skills_string_to_list(skills))
    return pd.DataFrame(
        [{"skill": skill, "count": count} for skill, count in counter.most_common(top_n)]
    )


def skill_cooccurrence(
    df: pd.DataFrame, top_n: int = 15, min_weight: int = 1
) -> pd.DataFrame:
    """Count skill pairs appearing in the same job (for a network graph)."""
    ranking = top_skills(df, top_n=top_n)
    popular = set(ranking["skill"])
    counter: Counter[tuple[str, str]] = Counter()
    for skills in df["skills"].dropna():
        present = [skill for skill in skills_string_to_list(skills) if skill in popular]
        for pair in combinations(sorted(present), 2):
            counter[pair] += 1
    edges = [
        {"source": source, "target": target, "weight": weight}
        for (source, target), weight in counter.items()
        if weight >= min_weight
    ]
    return pd.DataFrame(edges)
