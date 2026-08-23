# STATUS

Tracks the 8 Definition of Done items from [CLAUDE.md](CLAUDE.md). Updated by Claude Code as build progresses.

| # | Item | Status | Notes |
|---|---|---|---|
| 1 | dbt project on Databricks: staging → intermediate → tested marts for seller/funnel/GMV data | In Progress | Databricks connection confirmed working. Folder structure exists (`models/staging/`, `models/intermediate/`, `models/marts/`). `stg_sellers.sql` complete — `dbt run --select stg_sellers` passes (view built in `raw.stg_sellers`). No tests yet defined for `stg_sellers` (`dbt test --select stg_sellers` is a no-op); intermediate/marts and test coverage still pending. |
| 2 | GitHub Actions CI running `dbt test` on push, demonstrably fails on a broken PR | Not started | |
| 3 | Logistic regression churn-risk model + segment-driver interpretation layer, correlational language only | Not started | |
| 4 | GMV-at-risk quantification joined to risk segments | Not started | |
| 5 | One Tableau dashboard: who's at risk, GMV exposure, distinguishing characteristics, prioritization view | Not started | |
| 6 | Documentation: README + case-study page (Olist-saturation risk, B2B reframe, funnel-attribution limitation, associative-not-causal framing) | Not started | |
| 7 | (Stretch, optional) Temporal validation split | Not started | |
| 8 | (Stretch, optional) Minimum seller-activity threshold + churn-window sensitivity check | Not started | |
