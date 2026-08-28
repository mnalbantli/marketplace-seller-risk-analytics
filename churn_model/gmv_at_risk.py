"""
GMV-at-risk quantification — CLAUDE.md Definition-of-Done item 4.

IMPORTANT — two separate populations/purposes, do not conflate:
  1. train_churn_model.py's held-out 80/20 test-set metrics (accuracy,
     precision, recall, F1, ROC-AUC — see churn_model/results/
     baseline_run_2026-08-25.txt) remain the model's OFFICIAL performance
     numbers. This script does not recompute or re-report them.
  2. This script refits the SAME LogisticRegression pipeline (identical
     features, identical preprocessing — imported directly from
     train_churn_model.py, not reimplemented, so the two are guaranteed to
     match) on the FULL modeled population (all 2,970 sellers with a
     defined recency_days, i.e. excluding the 125 "never-activated"
     sellers per the same candidate decision as train_churn_model.py).
     Every seller then gets a predict_proba risk score generated
     consistently, rather than mixing in-sample scores (training sellers)
     with out-of-sample scores (test sellers) from a single 80/20 split.
     These risk scores are IN-SAMPLE by construction (the model has seen
     every seller's label) — they are used here only for GMV-weighting,
     not as a claim about the model's out-of-sample discriminative power.
     That claim is what item 1 above is for.

GMV-at-risk (probability-weighted):
    sum(predict_proba(seller) * seller.gmv) across all 2,970 modeled sellers

Compared against the earlier rough binary estimate — sum(seller.gmv) for
sellers with is_churned == 1 (the recency_days > 60 cutoff), divided by
total GMV — reproduced here directly from mart_seller_health, not
hardcoded, so it stays correct if the underlying data changes.

Rare-category bucketing (top_category, seller_state; MIN_CATEGORY_SAMPLES
= 20) is recomputed on the full 2,970-seller population for this refit,
using the same rule as train_churn_model.py but a different base
population (there is no train/test split here) — counts/affected rows are
printed at runtime and will differ slightly from the original 80%-train-
only counts.

Median order_count for the above/below-median breakdown (candidate
decision, 2026-08-26) is computed over the 2,970 modeled sellers — the
same population being scored. Split: order_count <= median -> "at-or-below
median"; order_count > median -> "above median".
"""

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from train_churn_model import (
    CATEGORICAL_FEATURES,
    MIN_CATEGORY_SAMPLES,
    NUMERIC_FEATURES,
    RARE_CATEGORY_BUCKET_COLUMNS,
    build_labeled_dataset,
    fetch_mart_seller_health,
    prepare_features,
)

REPO_ROOT = Path(__file__).resolve().parent


def bucket_rare_categories_full_population(
    df: pd.DataFrame, columns: list, min_samples: int
) -> pd.DataFrame:
    """Same MIN_CATEGORY_SAMPLES=20 rule as train_churn_model.py's
    bucket_rare_categories, but computed over the full population passed in
    (no train/test split exists for this full-data refit)."""
    df = df.copy()
    for col in columns:
        counts = df[col].value_counts()
        frequent = set(counts[counts >= min_samples].index)
        rare = set(counts[counts < min_samples].index)
        n_rows_bucketed = int(df[col].isin(rare).sum())
        print(
            f"  {col}: {len(rare)} of {len(counts)} categories fall below "
            f"MIN_CATEGORY_SAMPLES={min_samples} (full population), grouped "
            f"into 'other' — {n_rows_bucketed} rows affected"
        )
        df[col] = df[col].where(df[col].isin(frequent), "other")
    return df


def main() -> None:
    print("=" * 78)
    print("GMV-AT-RISK — full-data refit for scoring purposes only.")
    print(
        "Held-out test-set metrics (accuracy/precision/recall/F1/ROC-AUC) are "
        "NOT recomputed here — see churn_model/results/baseline_run_2026-08-25.txt "
        "for the official model-performance numbers."
    )
    print("=" * 78)

    raw = fetch_mart_seller_health()
    labeled = build_labeled_dataset(raw)
    labeled = prepare_features(labeled)

    print(
        f"\nRefitting on the full modeled population: n={len(labeled)} "
        "(all sellers with a defined recency_days; the 125 never-activated "
        "sellers above are excluded, same as train_churn_model.py)"
    )

    print("\nBucketing rare categories (full-population counts) into 'other':")
    labeled = bucket_rare_categories_full_population(
        labeled, RARE_CATEGORY_BUCKET_COLUMNS, MIN_CATEGORY_SAMPLES
    )

    X_full = labeled[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_full = labeled["is_churned"]

    # Identical pipeline shape/hyperparameters to train_churn_model.py —
    # only the fit population differs (full 2,970 vs. an 80% split).
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
    model.fit(X_full, y_full)

    labeled["risk_score"] = model.predict_proba(X_full)[:, 1]

    # --- Probability-weighted GMV-at-risk ---
    weighted_gmv_at_risk = (labeled["risk_score"] * labeled["gmv"]).sum()
    total_gmv = labeled["gmv"].sum()
    weighted_pct = weighted_gmv_at_risk / total_gmv

    # --- Earlier rough binary estimate, reproduced from the same data ---
    binary_gmv_at_risk = (labeled["is_churned"] * labeled["gmv"]).sum()
    binary_pct = binary_gmv_at_risk / total_gmv

    print("\n=== GMV-at-Risk: Probability-Weighted vs. Binary Cutoff ===")
    print(f"Total GMV across modeled population (n={len(labeled)}): ${total_gmv:,.2f}")
    print(
        f"\nBinary cutoff estimate (is_churned = recency_days > 60):\n"
        f"  GMV-at-risk: ${binary_gmv_at_risk:,.2f}  ({binary_pct:.1%} of total GMV)"
    )
    print(
        f"\nProbability-weighted estimate (full-data-refit predict_proba x gmv):\n"
        f"  GMV-at-risk: ${weighted_gmv_at_risk:,.2f}  ({weighted_pct:.1%} of total GMV)"
    )
    print(
        f"\nDifference: ${weighted_gmv_at_risk - binary_gmv_at_risk:,.2f} "
        f"({weighted_pct - binary_pct:+.1%} points) — the probability-weighted "
        "figure reflects each seller's individual predicted risk instead of "
        "treating every 'churned' seller as fully at-risk and every 'active' "
        "seller as not at-risk at all."
    )

    # --- Above/below median order_count breakdown ---
    median_order_count = labeled["order_count"].median()
    above_median = labeled["order_count"] > median_order_count
    at_or_below_median = ~above_median

    print(
        f"\n=== GMV-at-Risk by order_count vs. Marketplace Median "
        f"(median={median_order_count:.1f}, n={len(labeled)} modeled sellers) ==="
    )
    for label, mask in [
        ("At-or-below median order_count", at_or_below_median),
        ("Above median order_count", above_median),
    ]:
        subset = labeled.loc[mask]
        subset_gmv = subset["gmv"].sum()
        subset_weighted_risk = (subset["risk_score"] * subset["gmv"]).sum()
        subset_weighted_pct_of_own_gmv = (
            subset_weighted_risk / subset_gmv if subset_gmv else float("nan")
        )
        subset_share_of_total_weighted_risk = subset_weighted_risk / weighted_gmv_at_risk
        print(f"\n{label}:")
        print(f"  Sellers: {len(subset)}")
        print(f"  Total GMV: ${subset_gmv:,.2f}")
        print(
            f"  Probability-weighted GMV-at-risk: ${subset_weighted_risk:,.2f} "
            f"({subset_weighted_pct_of_own_gmv:.1%} of this bucket's own GMV)"
        )
        print(
            f"  Share of marketplace-wide weighted GMV-at-risk: "
            f"{subset_share_of_total_weighted_risk:.1%}"
        )

    print(
        "\n(For reference: PROCESS.md's 'Verified Finding' shows churned sellers "
        "average $2,881 GMV / 17.2 orders vs. active sellers' $9,980 GMV / 88.4 "
        "orders — the breakdown above tests whether that concentration among "
        "low-volume sellers holds when weighted by continuous risk probability "
        "instead of the binary churned/active label.)"
    )


if __name__ == "__main__":
    main()
