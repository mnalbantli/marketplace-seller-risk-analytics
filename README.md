# Marketplace Seller Risk Analytics

> Pipeline (dbt on Databricks), churn model (logistic regression), GMV-at-risk quantification, and Tableau dashboard are complete. Pipeline-architecture and how-to-reproduce sections are still to follow.

## Business Context

Olist is a Brazilian platform that connects small and medium-sized businesses to online marketplaces through a single contract. Rather than a shopkeeper independently setting up on multiple marketplaces (like Mercado Livre or Americanas), Olist handles listing, order routing, and logistics on their behalf. Founded in 2015, the platform's core mission is lowering the technical and logistical barrier for small merchants to sell online.

This project uses Olist's public, anonymized dataset covering orders from January 2017 to August 2018, an early window in the platform's growth. By later years, Olist had scaled to tens of thousands of merchant clients; this dataset captures roughly 3,095 sellers, a much earlier and smaller cohort.

**Why this matters for the analysis:** the seller population in this dataset is not uniform. It's split between a large group of newly onboarded shopkeepers still testing the platform (many placing only a handful of orders) and a smaller group of established merchants who had already scaled their presence. This bimodal shape is a real reflection of an early-stage marketplace's growth pattern, not a data quality issue, and it directly shapes how "at-risk" is defined and measured in this project (see PROCESS.md for the full reasoning behind the low-history / established seller split).

This project analyzes seller-side risk and retention, not individual end-customer behavior.

Most public analyses of the Olist dataset focus on customer-side churn. This project reframes it around B2B sellers, the actual accounts transacting on the platform, a less common angle on a widely-used dataset.

A known limitation: only ~380 of the transacting seller population have acquisition-channel data (funnel attribution), and category data is unavailable for a small subset of sellers. These gaps are disclosed and handled explicitly throughout; nulls are never imputed. Full methodology in PROCESS.md.

## Key Findings

(assets/dashboard_screenshot.png)


All findings below are **associative, not causal**. They describe characteristics that correlate with elevated churn risk, not proven drivers of it. Full detail and methodology for each finding: [PROCESS.md](mds/PROCESS.md).

**High-volume sellers hold 87.4% of at-risk GMV dollars, even though low-volume sellers churn at a much higher rate.** Low-volume sellers churn at 85.7% (their own GMV at risk), versus 47.5% for high-volume sellers. But high-volume sellers hold 93% of total marketplace GMV ($12.2M of $13.2M), so their lower risk rate still translates into 87.4% of total at-risk dollars, versus only 12.6% for the low-volume group. Both are true simultaneously, and they answer different business questions: *who is most likely to churn* (low-volume sellers) vs. *where retention budget should actually go* (high-volume sellers, since that's where the dollar exposure sits).

**Order volume is the strongest associative pattern.** Churned sellers average $2,881 GMV and 17.2 orders; active sellers average $9,980 GMV and 88.4 orders. Active sellers show roughly 3.5x the GMV and 5x the order count of churned sellers. This is the model's strongest coefficient, independently corroborated by a direct group comparison rather than model output alone.

**Geography: a São Paulo effect, not a broad geographic spread.** Among the 9 seller states with enough sellers to measure reliably (20+ sellers each), São Paulo (60% of all sellers) shows a 41.88% risk rate, versus 65.72% for the other 8 states combined, a ~24-point gap. This looks like a genuine "SP vs. everywhere else" pattern rather than risk spread evenly across many states. One hypothesis, not yet confirmed: this may reflect São Paulo's position as Brazil's primary commercial/logistics hub rather than geography itself, a possible proxy for fulfillment infrastructure quality.

**Model performance.** A baseline logistic regression, trained on 2,970 sellers with an observed order history (125 "never-activated" sellers with no delivered orders are excluded, a structurally different population, not comparable to a seller who transacted and then went quiet), reaches 80.1% accuracy against a 77.9% baseline churn rate, only marginally above what a model that always predicted "churned" would score. ROC-AUC of 0.746 is the more honest measure of the model's real discriminative power, independent of the class imbalance. This is a deliberately minimal, single-fit baseline (no hyperparameter tuning, no cross-validation loop), a real but modest signal, not a strong classifier.

## Dashboard

[Live Tableau dashboard](https://public.tableau.com/app/profile/mustafa.nalbantli/viz/Dashboard_17881927167970/Dashboard?publish=yes): who's at risk, GMV exposure, distinguishing characteristics, and a prioritization view.

---

## Technical Details

| Term | Meaning |
|---|---|
| **Seller** | A small/medium business (shopkeeper) selling through Olist, the "B2B account" this project analyzes |
| **Order** | A purchase transaction placed by an end customer, which can include items from one or more sellers |
| **Order item** | One product line within an order, tied to the specific seller who fulfilled it |

Pipeline architecture, driver-selection rationale, and full analytical methodology: see [CLAUDE.md](mds/CLAUDE.md) and [PROCESS.md](mds/PROCESS.md).

*(Sections to follow: pipeline architecture, how to reproduce.)*
