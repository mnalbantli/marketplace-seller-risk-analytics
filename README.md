# Marketplace Seller Risk Analytics

> **Status: Draft in progress.** This README will be completed as part of the final documentation deliverable (Item 6 in CLAUDE.md's Definition of Done), once the pipeline, model, and dashboard are complete. The section below is written early, while the context is fresh.

## Business Context

Olist is a Brazilian platform that connects small and medium-sized businesses to online marketplaces through a single contract — rather than a shopkeeper independently setting up on multiple marketplaces (like Mercado Livre or Americanas), Olist handles listing, order routing, and logistics on their behalf. Founded in 2015, the platform's core mission is lowering the technical and logistical barrier for small merchants to sell online.

This project uses Olist's public, anonymized dataset covering orders from January 2017 to August 2018 — an early window in the platform's growth. By later years, Olist had scaled to tens of thousands of merchant clients; this dataset captures roughly 3,095 sellers, a much earlier and smaller cohort.

**Why this matters for the analysis:** the seller population in this dataset is not uniform. It's split between a large group of newly onboarded shopkeepers still testing the platform (many placing only a handful of orders) and a smaller group of established merchants who had already scaled their presence. This bimodal shape is a real reflection of an early-stage marketplace's growth pattern — not a data quality issue — and it directly shapes how "at-risk" is defined and measured in this project (see PROCESS.md for the full reasoning behind the low-history / established seller split).

## Who's Who in This Data

| Term | Meaning |
|---|---|
| **Seller** | A small/medium business (shopkeeper) selling through Olist — the "B2B account" this project analyzes |
| **Order** | A purchase transaction placed by an end customer, which can include items from one or more sellers |
| **Order item** | One product line within an order, tied to the specific seller who fulfilled it |

This project analyzes seller-side risk and retention — not individual end-customer behavior.

---

*(Sections to follow once complete: pipeline architecture, how to reproduce, key findings, dashboard link.)*
