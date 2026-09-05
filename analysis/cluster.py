"""KMeans clustering of job descriptions via TF-IDF vectors."""

from __future__ import annotations

from collections import Counter

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score

from analysis.text_features import tokenize
from cleaner.skills import skills_string_to_list


def cluster_jobs(df: pd.DataFrame, k: int = 4) -> pd.DataFrame:
    """Cluster jobs by description text; store silhouette in ``df.attrs``."""
    text = (
        df["title"].fillna("")
        + " "
        + df["description"].fillna("")
        + " "
        + df["skills"].fillna("")
    )
    vectorizer = TfidfVectorizer(tokenizer=tokenize)
    matrix = vectorizer.fit_transform(text)

    cluster_count = min(k, max(2, matrix.shape[0]))
    model = KMeans(n_clusters=cluster_count, random_state=42, n_init=10)
    labels = model.fit_predict(matrix)

    result = df.copy()
    result["cluster"] = labels
    silhouette = (
        float(silhouette_score(matrix, labels))
        if cluster_count > 1 and matrix.shape[0] > cluster_count
        else 0.0
    )
    result.attrs["silhouette"] = silhouette
    result.attrs["cluster_count"] = cluster_count
    return result


def cluster_profiles(clustered: pd.DataFrame, top_skills_n: int = 5) -> pd.DataFrame:
    """Summarize each cluster with job count, salary and top skills."""
    rows: list[dict[str, object]] = []
    for label, group in clustered.groupby("cluster"):
        skill_counter: Counter[str] = Counter()
        for skills in group["skills"].dropna():
            skill_counter.update(skills_string_to_list(skills))
        top_skills = [skill for skill, _ in skill_counter.most_common(top_skills_n)]
        avg_salary = group["salary_avg"].mean()
        rows.append(
            {
                "cluster": int(label),
                "job_count": int(len(group)),
                "avg_salary": round(float(avg_salary), 2) if pd.notna(avg_salary) else None,
                "top_skills": ", ".join(top_skills),
            }
        )
    return pd.DataFrame(rows)
