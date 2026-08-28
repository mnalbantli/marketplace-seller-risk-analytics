## Data Structure Discovery: `products` Table
Initial assumption: `order_items` already carried product attributes 
(same columns present), making a separate `products` model redundant.
Verification (aggregate null check) showed the opposite: `product_category_name` 
is NULL on every real order row in `order_items` — populated only on 
32,951 disconnected phantom rows with no order_id. `products` is the only 
real source for category data on actual transactions. Kept as a separate 
staged model, joined in intermediate.

# Driver Selection — Process & Rationale

## Business Question
Which B2B marketplace seller segments are at risk of churning, and what
observable, associative patterns characterize that risk?

## Screening Criteria for Candidate Drivers
1. **Coverage** — does this variable exist for most sellers, or a small subset?
2. **Confounding risk** — could this be a proxy for something else, not a real driver?
3. **Actionability** — if real, can the business actually act on it?
4. **Cost to compute** — already staged, or needs new derivation?

## Candidates Considered

| Driver | Coverage | Confounding Risk | Actionability | Decision |
|---|---|---|---|---|
| Acquisition channel | ~27% (842/3,095) | High — attributed sellers are self-selected | Medium | **Secondary, explicitly caveated — not a headline driver** |
| Product category | 100% | Lower | High | **Primary** |
| Geography | 100% | Medium — likely a proxy for freight/fulfillment | High, with mechanism | **Primary, paired with fulfillment data** |
| Seller tenure | 100% | Low | Medium | **Primary** |
| Order frequency trend | 100% | Low — closest to directly causal | High | **Primary** |

## Final Driver Set
- Product category mix
- Geography (state/city)
- Seller tenure (time since first order)
- Order frequency trend (declining vs. stable cadence)
- Acquisition channel — included as a secondary lens, restricted to the
  27% funnel-attributed subset, with selection bias disclosed

## Why This Matters
Coverage was the deciding factor over personal interest or intuition — a
driver that only exists for a quarter of the population can't support a
platform-wide "why," no matter how interesting it is.

## Note on Reasoning: Correlational, Not Causal
Per CLAUDE.md's locked framing discipline — every driver above is an
associative pattern candidate, not a proven cause of churn. Final writeups
must state findings as "sellers with X characteristic show elevated churn
risk," never "X causes churn."

## Category Concentration — NULL Handling
Checked GMV exposure of NULL-category order_items before deciding to exclude 
them: NULL-category items account for ~1.3% of total marketplace GMV 
(179,535 / 13,591,644). Excluding them entirely (numerator and denominator) 
from category concentration calculations is a safe simplification — the 
excluded volume is small enough that it won't materially distort any 
seller's concentration score, except potentially for a small number of 
individual sellers with unusually high NULL-category exposure (not yet 
checked at the seller level — worth a caveat if a specific seller's 
concentration score looks unreliable during driver analysis).

## Verified Finding: Churn (recency > 60d) Concentrates Among Low-Volume Sellers
Direct comparison (2026-08-26), not inferred:
| Status | Sellers | Avg GMV | Avg Order Count |
| Churned | 2,313 | $2,881 | 17.2 |
| Active | 657 | $9,980 | 88.4 |

Active sellers average ~3.5x the GMV and ~5x the order count of churned 
sellers. This corroborates the model's strongest coefficient (order_count) 
independently, via a direct group comparison rather than model output alone.

## GMV-at-Risk: Rate vs. Dollar Concentration Diverge
Low-volume sellers churn at a much higher rate (85.7% of their own GMV at 
risk vs. 47.5% for high-volume sellers) — confirming the earlier per-seller 
finding. But high-volume sellers hold 93% of total marketplace GMV ($12.2M 
of $13.2M), so even their lower risk rate translates to 87.4% of total 
dollars at risk, versus only 12.6% for the low-volume group.

Both are correct simultaneously — a large percentage of a small pile is 
still a smaller dollar figure than a small percentage of a huge pile. They 
answer different business questions: "who is most likely to churn" (low-
volume sellers) vs. "where should retention budget actually go" (high-
volume sellers, since that's where the dollar exposure sits).
