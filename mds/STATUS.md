# STATUS

Tracks the 8 Definition of Done items from [CLAUDE.md](CLAUDE.md). Updated by Claude Code as build progresses.

| # | Item | Status | Notes |
|---|---|---|---|
| 1 | dbt project on Databricks: staging → intermediate → tested marts for seller/funnel/GMV data | In Progress | Five staging models built and tested: `stg_sellers`, `stg_orders`, `stg_products`, `stg_category_translation`, `stg_order_items` — all in `models/staging/`, all passing (`dbt test`, 2026-08-23, 7/7 PASS on the latest on top of the earlier 10/10). `stg_products` and `stg_category_translation` rename `product_category_name`→`category_name` (and `_english` variant) for a `USING(category_name)` join. `product_category_translation` is a `dbt seed` from the real Olist CSV, referenced via `ref()` not `source()`. `stg_order_items` — the orders↔sellers join point and GMV source (`price`, `freight_value`) — filters `WHERE order_id IS NOT NULL` to drop ~32,951 join/union-artifact rows found upstream in the raw table, drops `shipping_limit_date` and 8 dead product-attribute columns (all NULL on real rows), and its `(order_id, order_item_id)` grain is checked with a singular test (`tests/assert_stg_order_items_unique_grain.sql`, no `dbt_utils` dependency added). `models/example/` scaffold removed; `dbt_project.yml` cleaned up. All of the above is **committed and pushed** to `origin/master` (commit `3e062b4`, on top of `8e91ff4` → `0ea8f9d` → `c737d26` → `36e6910` → `b3f47de`). **Databricks workspace migration (2026-08-24): data re-uploaded to a new workspace; `dbt run` + `dbt test` re-verified against it for all four core staging models — `stg_sellers` (1/1 PASS), `stg_orders` (3/3 PASS), `stg_order_items` (8/8 PASS), `stg_products` (2/2 PASS) — 4/4 models built, 14/14 tests green. No model logic changed; only the underlying connection/workspace.** `intermediate/` and `marts/` are still empty — no models there yet. Untracked `LESSONS.md` exists at repo root (candidate's own file, not committed by Claude Code). |
| 2 | GitHub Actions CI running `dbt test` on push, demonstrably fails on a broken PR | Not started | |
| 3 | Logistic regression churn-risk model + segment-driver interpretation layer, correlational language only | Not started | |
| 4 | GMV-at-risk quantification joined to risk segments | Not started | |
| 5 | One Tableau dashboard: who's at risk, GMV exposure, distinguishing characteristics, prioritization view | Not started | |
| 6 | Documentation: README + case-study page (Olist-saturation risk, B2B reframe, funnel-attribution limitation, associative-not-causal framing) | Not started | |
| 7 | (Stretch, optional) Temporal validation split | Not started | |
| 8 | (Stretch, optional) Minimum seller-activity threshold + churn-window sensitivity check | Not started | |
