"""Content-based job recommendation using TF-IDF cosine similarity."""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from analysis.text_features import tokenize

EDUCATION_LEVEL = {"不限": 0, "大专": 1, "本科": 2, "硕士": 3, "博士": 4}

RESULT_COLUMNS = ["title", "company", "city", "education", "salary_avg", "match_score", "link"]


def recommend_jobs(
    df: pd.DataFrame,
    profile: dict[str, Any],
    top_n: int = 5,
) -> pd.DataFrame:
    """Rank jobs for a user profile; hard filters run before similarity."""
    query_text = profile.get("skills", "")
    city = profile.get("city")
    education = profile.get("education")
    salary_max = profile.get("salary_max")

    candidates = df.copy()
    if city:
        candidates = candidates[candidates["city"] == city]
    if education and education in EDUCATION_LEVEL:
        user_level = EDUCATION_LEVEL[education]
        job_levels = candidates["education"].map(EDUCATION_LEVEL.get).fillna(0)
        candidates = candidates[job_levels <= user_level]
    if salary_max and "salary_avg" in candidates.columns:
        candidates = candidates[candidates["salary_avg"].fillna(0) <= salary_max]

    if candidates.empty:
        return pd.DataFrame(columns=RESULT_COLUMNS)

    text = (
        candidates["title"].fillna("")
        + " "
        + candidates["description"].fillna("")
        + " "
        + candidates["skills"].fillna("")
    )
    vectorizer = TfidfVectorizer(tokenizer=tokenize)
    matrix = vectorizer.fit_transform(text)
    query_vec = vectorizer.transform([str(query_text)])
    scores = cosine_similarity(query_vec, matrix).ravel()

    result = candidates.copy()
    result["match_score"] = scores.round(4)
    result = result.sort_values("match_score", ascending=False).head(top_n)
    return result[RESULT_COLUMNS].reset_index(drop=True)
