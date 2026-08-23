# Project: B2B Marketplace Seller Risk Analytics

## STATUS: SCOPE LOCKED — 2026-08-19. Do not modify this file's scope sections without an explicit, deliberate re-scoping conversation. Adding items here mid-build is scope creep and should be refused by default.

---

## Business Question (Stage 0 — Fixed)

> Which B2B marketplace seller segments are at risk of churning, and what observable, associative patterns characterize that risk?

Note the deliberate wording: **associative, not causal.** The model can establish "these characteristics correlate with elevated churn risk," not "X causes churn." State this explicitly in all documentation and dashboard copy. This is the same statistical discipline that retired "genuine incremental lift" language on the Mean Mug project — apply it proactively here, not retroactively.

## Context

- Second and final major portfolio project. First project ("Mean Mug," B2C coffee-shop analytics: dbt, BigQuery, Power BI, RFM, cohort retention, LTV, Welch's t-test/Glass's Δ) is retired and not touched further.
- Candidate: MS Data Analytics student, international (F-1/OPT→H-1B change-of-status path), graduating Dec 2026. Primary target: Data Analyst roles, retail/consumer/marketplace analytics. Analytics Engineer is an aspirational next-role narrative, not a today-eligible title.
- This document was locked after an independent 3-model evaluation ("council" exercise) converged on a scope correction from the original plan. That correction is reflected below — this is not the first draft.

## Domain & Data (Locked)

- **Business model: B2B.** Sellers are the analytical unit ("accounts"), not shoppers.
- **Industry: Retail / marketplace / wholesale-adjacent.**
- **Dataset: Real Olist Brazilian e-commerce data.** No fabricated or relabeled data, ever.
- **Known, disclosed limitation:** only ~842 of ~3,000+ sellers have marketing-funnel/acquisition-channel attribution. The remaining ~2,158 are left NULL — never imputed, never silently dropped. This gap is itself a documented analytical finding (potential selection bias in funnel coverage), not just a caveat.
- **Differentiator to state explicitly in the README:** most public Olist projects analyze customer-side churn. This project reframes the same dataset around B2B seller/merchant risk — name this contrast directly, since Olist is a widely-recognized, saturated dataset and the reframe is what earns attention past that recognition.

## Tool Stack — Final, Post-Council (Locked)

| Tool | Status | Role |
|---|---|---|
| Databricks | **Keep** | Compute/warehouse — timebox setup hard; if it eats >4 hrs, fall back to BigQuery |
| dbt | **Keep** | Staging → intermediate → mart, reused pattern from Mean Mug |
| GitHub Actions | **Keep** | CI — `dbt test` on every push, fails loudly on breakage |
| Logistic regression | **Keep** | Reused pattern from prior dropout-prediction project. No new model family (no XGBoost). |
| Tableau | **Keep** | Single presentation layer — the only dashboard/interface built |
| ~~Streamlit~~ | **CUT** | Redundant with Tableau; no council evaluator supported building both |
| ~~Dagster~~ | **CUT** | Orchestrating a static/replayed dataset is infrastructure theater; not probed by target-role interviews |
| ~~Docker~~ | **CUT** | Decoration for this scope; not a Platform Engineer application |

## Required Analytical Additions (Not Tool Additions)

1. **GMV-at-risk layer:** risk score × seller GMV exposure. Label explicitly as "GMV exposure," never "revenue loss" or "profit impact" — no margin/profit data exists.
2. **Correlational-language discipline:** every "why" output framed as diagnostic/associative evidence, never causal claims.
3. **Stretch, time-permitting only:** temporal train/predict split (train on early period, predict subsequent period) instead of random split.

## Definition of Done (8 Items — Nothing Beyond This List)

1. dbt project on Databricks: staging → intermediate → tested marts for seller/funnel/GMV data
2. GitHub Actions CI running `dbt test` on push, demonstrably fails on a broken PR
3. Logistic regression churn-risk model + segment-driver interpretation layer, correlational language only
4. GMV-at-risk quantification joined to risk segments
5. One Tableau dashboard: who's at risk, GMV exposure, distinguishing characteristics, prioritization view
6. Documentation: README + case-study page naming the Olist-saturation risk, the B2B reframe, the funnel-attribution limitation, and the associative-not-causal framing
7. (Stretch, optional) Temporal validation split
8. (Stretch, optional) Minimum seller-activity threshold + explicit churn-window sensitivity check

## Time Budget

6 weeks, ~8 hours/week, ~48 hours total. Non-negotiable. If a deliverable isn't done at week 6, it goes to the cut list below — the timeline does not extend.

## Cut List (First Things Dropped If Time Runs Short)

1. Temporal validation split (Item 7 above)
2. Churn-window sensitivity check (Item 8 above)
3. Any additional dataset joins beyond core Olist tables
4. Multi-brand/white-label config (only a single neutral demo brand is in scope)

## Explicitly Rejected (Do Not Revisit)

- Fabricating or relabeling B2C data as B2B
- Publicly branding the tool with a real target company's name/logo (private, 1:1 outreach only, never public)
- Randomly generated synthetic "live" data (a disclosed, compressed-timeline replay of real historical data is the only acceptable "live" mechanism, and it is NOT in the current Definition of Done — it was cut with Streamlit)
- XGBoost or any new ML model family
- A second BI tool alongside Tableau
- Docker, Dagster (see Tool Stack table — cut post-council, do not re-add without a full re-scoping conversation)
- Adding a 4th+ evaluator/council round or new external validation tooling to re-litigate this scope document itself

## Workflow / Role Split

- **Candidate writes all dbt models and modeling logic themselves** — this is the ownership and skill-building the project exists to build. Do not let Claude Code originate business logic or modeling decisions.
- **Claude Code's job:** scaffold repo structure, run `dbt build`/`dbt test`, fix syntax-level errors, git add/commit/push with clear descriptive messages, maintain `STATUS.md` tracking which Definition-of-Done items are done/in-progress/not-started.
- **Chat-based Claude's job:** sanity-check modeling logic and business-question alignment before/after each stage, hold this scope document's boundary against additions.
- Git commit history is the progress log. No separate journal needed beyond `STATUS.md`.

## Standing Instruction (Confirmed by Candidate, Applies to Claude Code Too)

If a new tool, model, dataset, presentation layer, or "one more evaluation round" is proposed mid-build that is not in the Definition of Done above: say **"that's scope creep — we agreed this is done,"** point back to this document, and log the idea in a `future-ideas.md` file instead of building it now. This applies even under direct pushback in the moment — that instruction was given in advance, deliberately, for exactly this scenario.
