# STATUS

Tracks the 8 Definition of Done items from [CLAUDE.md](CLAUDE.md). Updated by Claude Code as build progresses.

| # | Item | Status | Notes |
|---|---|---|---|
| 1 | dbt project on Databricks: staging → intermediate → tested marts for seller/funnel/GMV data | In Progress | Databricks connection confirmed working. `stg_sellers.sql` and `stg_orders.sql` both written in `models/staging/`, with `schema.yml` defining tests for both. All tests confirmed passing: `stg_sellers` — unique + not_null on `seller_id` (`dbt test --select stg_sellers`, 2026-08-22 20:54 local, 2/2 PASS); `stg_orders` — unique + not_null on `order_id`, accepted_values on `order_status` (`dbt test --select stg_orders`, 2026-08-22 20:49 local, 3/3 PASS). `models/example/` scaffold removed. All of the above is **committed and pushed** to `origin/master` (commit `36e6910`, on top of `b3f47de`). Stale `dbt_project.yml` config block (`models.olist_seller_risk.example`) referencing the deleted `example/` folder has been cleaned up — `dbt parse` no longer warns about unused configuration paths. `intermediate/` and `marts/` are still empty — no models there yet. |
| 2 | GitHub Actions CI running `dbt test` on push, demonstrably fails on a broken PR | Not started | |
| 3 | Logistic regression churn-risk model + segment-driver interpretation layer, correlational language only | Not started | |
| 4 | GMV-at-risk quantification joined to risk segments | Not started | |
| 5 | One Tableau dashboard: who's at risk, GMV exposure, distinguishing characteristics, prioritization view | Not started | |
| 6 | Documentation: README + case-study page (Olist-saturation risk, B2B reframe, funnel-attribution limitation, associative-not-causal framing) | Not started | |
| 7 | (Stretch, optional) Temporal validation split | Not started | |
| 8 | (Stretch, optional) Minimum seller-activity threshold + churn-window sensitivity check | Not started | |
