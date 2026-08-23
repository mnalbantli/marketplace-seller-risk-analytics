# STATUS

Tracks the 8 Definition of Done items from [CLAUDE.md](CLAUDE.md). Updated by Claude Code as build progresses.

| # | Item | Status | Notes |
|---|---|---|---|
| 1 | dbt project on Databricks: staging → intermediate → tested marts for seller/funnel/GMV data | In Progress | Four staging models built and tested: `stg_sellers`, `stg_orders`, `stg_products`, `stg_category_translation` — all in `models/staging/`, all passing (`dbt test`, 2026-08-23, 5/5 PASS on the latest two on top of the earlier 5/5). `stg_products` and `stg_category_translation` both rename `product_category_name`→`category_name` (and `_english` variant) so a later join can use `USING(category_name)`. `product_category_translation` (the real Olist CSV, unmodified) is loaded via `dbt seed` into `raw.product_category_translation` — dbt-managed, referenced with `ref()`, not `source()`, and correctly *not* listed in `source.yml` (which only covers externally-loaded raw tables). Known data-quality notes carried into the model docs: `raw.order_items` product-attribute columns (incl. category) are NULL on every real order row — `stg_products`/`stg_category_translation` are the only path to category data, and `category_name` is NULL for ~610 products with no imputation. `models/example/` scaffold removed; `dbt_project.yml`'s stale config for it cleaned up. All of the above is **committed and pushed** to `origin/master` (commit `0ea8f9d`, on top of `c737d26` → `36e6910` → `b3f47de`). `intermediate/` and `marts/` are still empty — no models there yet. |
| 2 | GitHub Actions CI running `dbt test` on push, demonstrably fails on a broken PR | Not started | |
| 3 | Logistic regression churn-risk model + segment-driver interpretation layer, correlational language only | Not started | |
| 4 | GMV-at-risk quantification joined to risk segments | Not started | |
| 5 | One Tableau dashboard: who's at risk, GMV exposure, distinguishing characteristics, prioritization view | Not started | |
| 6 | Documentation: README + case-study page (Olist-saturation risk, B2B reframe, funnel-attribution limitation, associative-not-causal framing) | Not started | |
| 7 | (Stretch, optional) Temporal validation split | Not started | |
| 8 | (Stretch, optional) Minimum seller-activity threshold + churn-window sensitivity check | Not started | |
