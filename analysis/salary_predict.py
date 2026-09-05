"""RandomForest salary prediction with ordinal categorical encoding."""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

NUMERIC_COLUMNS = ["skill_count"]
CATEGORICAL_COLUMNS = ["education", "experience", "company_size", "city"]
FEATURE_COLUMNS = NUMERIC_COLUMNS + CATEGORICAL_COLUMNS


def _build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", NUMERIC_COLUMNS),
            (
                "cat",
                OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
                CATEGORICAL_COLUMNS,
            ),
        ]
    )
    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", RandomForestRegressor(random_state=42, n_estimators=120)),
        ]
    )


def train_salary_model(
    df: pd.DataFrame, test_size: float = 0.2
) -> tuple[Pipeline, dict[str, Any]]:
    """Train salary prediction on cleaned jobs; return (pipeline, metrics)."""
    data = df.dropna(subset=["salary_avg"]).copy()
    y = data["salary_avg"].astype(float)
    x = data[FEATURE_COLUMNS].copy()
    for column in CATEGORICAL_COLUMNS:
        x[column] = x[column].fillna("不限")
    x[NUMERIC_COLUMNS] = x[NUMERIC_COLUMNS].fillna(0)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=42
    )
    pipeline = _build_pipeline()
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)

    feature_names = pipeline.named_steps["preprocess"].get_feature_names_out()
    importance = pipeline.named_steps["model"].feature_importances_
    metrics: dict[str, Any] = {
        "mae": float(mean_absolute_error(y_test, predictions)),
        "r2": float(r2_score(y_test, predictions)),
        "train_size": int(len(x_train)),
        "test_size": int(len(x_test)),
        "feature_importance": {
            name: float(weight)
            for name, weight in sorted(
                zip(feature_names, importance, strict=True),
                key=lambda pair: pair[1],
                reverse=True,
            )
        },
    }
    return pipeline, metrics


def predict_salary(pipeline: Pipeline, sample: pd.Series | dict[str, Any]) -> float:
    """Predict monthly salary (K) for a single job row."""
    row = pd.DataFrame([sample])[FEATURE_COLUMNS]
    for column in CATEGORICAL_COLUMNS:
        row[column] = row[column].fillna("不限")
    for column in NUMERIC_COLUMNS:
        row[column] = row[column].fillna(0)
    return float(pipeline.predict(row)[0])
