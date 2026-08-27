"""
Churn-risk baseline model — CLAUDE.md Definition-of-Done item 3.

Scope, deliberately minimal per candidate instruction: one model, one
stratified 80/20 split, no hyperparameter tuning, no cross-validation loop,
no threshold optimization. This is a single clean baseline fit, not an
iteration loop.

Label:
    is_churned = 1 if recency_days > 60 else 0

Sellers with recency_days IS NULL (no delivered orders ever) are excluded
from train/test entirely — "never-activated" is a structurally different
population from "went quiet after being active." Candidate decision,
2026-08-25; document the excluded count in PROCESS.md as its own segment.

Leakage prevention: recency_days, trend_eligible, orders_last_30d, and
orders_prior_30d are used ONLY to construct the label above. None of them
appear in the feature set — including any of them as a feature would let
the model trivially reverse-engineer the label instead of learning a real
pattern.

Feature encoding decisions (candidate-confirmed, 2026-08-25):
  - seller_city dropped entirely (611 distinct values relative to ~3,000
    rows — one-hot would create near-empty columns). seller_state (23
    distinct values) kept as the geography feature.
  - top_category kept at full granularity (69 distinct values) — primary
    driver per PROCESS.md, not collapsed preemptively.
  - Categorical NULLs (origin, top_category) encoded as an explicit
    "missing" category level, not dropped or imputed to a real category.
  - category_concentration_pct: NULLs get an explicit
    category_concentration_pct_missing indicator (1/0), then the
    underlying NULL is imputed to 0 only after that flag exists.
"""

import json
import subprocess
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

REPO_ROOT = Path(__file__).resolve().parents[1]
DBT_PROJECT_DIR = REPO_ROOT / "olist_seller_risk"

NUMERIC_FEATURES = [
    "gmv",
    "order_count",
    "cancellation_rate",
    "unresolved_rate",
    "category_concentration_pct",
    "category_concentration_pct_missing",
]
CATEGORICAL_FEATURES = ["top_category", "origin", "seller_state"]


def fetch_mart_seller_health() -> pd.DataFrame:
    """Pull mart_seller_health fresh from Databricks via `dbt show`."""
    result = subprocess.run(
        [
            "dbt", "show",
            "--select", "mart_seller_health",
            "--output", "json",
            "--limit", "-1",
            "--quiet",
        ],
        cwd=DBT_PROJECT_DIR,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    return pd.DataFrame(payload["show"])


def build_labeled_dataset(df: pd.DataFrame) -> pd.DataFrame:
    total = len(df)
    never_activated = df["recency_days"].isna()
    excluded = int(never_activated.sum())
    print(f"Total sellers in mart_seller_health: {total}")
    print(
        f"Excluding {excluded} 'never-activated' sellers (recency_days IS NULL — "
        "no delivered orders ever) from train/test entirely."
    )
    df = df.loc[~never_activated].copy()
    df["is_churned"] = (df["recency_days"] > 60).astype(int)
    return df


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["category_concentration_pct_missing"] = df["category_concentration_pct"].isna().astype(int)
    df["category_concentration_pct"] = df["category_concentration_pct"].fillna(0.0)
    df["top_category"] = df["top_category"].fillna("missing")
    df["origin"] = df["origin"].fillna("missing")
    return df


def report_top_coefficient_support(
    model: Pipeline,
    feature_names,
    coefficients,
    X_train: pd.DataFrame,
    labeled: pd.DataFrame,
    top_n: int = 8,
) -> None:
    """For the top-N coefficients by |magnitude|, report how many sellers
    actually carry that feature value — small-sample categories can produce
    large, noisy coefficients that don't reflect a real pattern."""
    cat_encoder = model.named_steps["preprocess"].named_transformers_["cat"]
    category_lookup = {}
    for col, categories in zip(CATEGORICAL_FEATURES, cat_encoder.categories_):
        for value in categories:
            category_lookup[f"cat__{col}_{value}"] = (col, value)

    ranked = sorted(zip(feature_names, coefficients), key=lambda x: -abs(x[1]))[:top_n]

    print(f"\n=== Sample Size Behind the Top {top_n} Coefficients (by |magnitude|) ===")
    print(f"{'feature':50s} {'coef':>8s} {'n_train':>8s} {'n_total':>8s}")
    for name, coef in ranked:
        if name in category_lookup:
            col, value = category_lookup[name]
            n_train = int((X_train[col] == value).sum())
            n_total = int((labeled[col] == value).sum())
            print(f"{name:50s} {coef:8.4f} {n_train:8d} {n_total:8d}")
        else:
            # continuous numeric feature — no subgroup to count; report full
            # split sizes so it's clear this row isn't a small-sample category
            print(f"{name:50s} {coef:8.4f} {len(X_train):8d} {len(labeled):8d}  (continuous, full n shown)")


def main() -> None:
    raw = fetch_mart_seller_health()
    labeled = build_labeled_dataset(raw)
    labeled = prepare_features(labeled)

    baseline_churn_rate = labeled["is_churned"].mean()
    print(
        f"Baseline churn rate (post-exclusion population, n={len(labeled)}): "
        f"{baseline_churn_rate:.1%} labeled churned"
    )

    X = labeled[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = labeled["is_churned"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )

    # StandardScaler on numeric features is a standard preprocessing step for
    # logistic regression (keeps convergence stable, puts coefficients on a
    # comparable scale) — not a tuning choice.
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("logreg", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    print("\n=== Baseline Logistic Regression — Test Set Metrics ===")
    print(f"Test set size: {len(y_test)} (stratified 80/20 split, random_state=42)")
    print(f"Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred):.4f}")
    print(f"Recall:    {recall_score(y_test, y_pred):.4f}")
    print(f"F1:        {f1_score(y_test, y_pred):.4f}")
    print(f"ROC-AUC:   {roc_auc_score(y_test, y_proba):.4f}")

    cm = confusion_matrix(y_test, y_pred)
    print("\nConfusion matrix (rows=actual, cols=predicted; class order [0, 1]):")
    print(cm)

    print(
        f"\nBaseline churn rate for context: {baseline_churn_rate:.1%} of the "
        f"{len(labeled)} modeled sellers are labeled churned — read accuracy "
        "against this, not against 50%."
    )

    feature_names = model.named_steps["preprocess"].get_feature_names_out()
    coefficients = model.named_steps["logreg"].coef_[0]
    intercept = model.named_steps["logreg"].intercept_[0]

    print("\n=== Coefficients (standardized numeric features; not yet interpreted) ===")
    print(f"{'feature':50s} coefficient")
    print(f"{'intercept':50s} {intercept: .4f}")
    for name, coef in sorted(zip(feature_names, coefficients), key=lambda x: -abs(x[1])):
        print(f"{name:50s} {coef: .4f}")

    report_top_coefficient_support(model, feature_names, coefficients, X_train, labeled, top_n=8)


if __name__ == "__main__":
    main()
