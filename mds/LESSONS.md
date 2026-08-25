# Lessons Learned

## 08/23/2026 - Composite keys / grain
**What I hit:** stg_order_items has no single-column primary key — order_id 
repeats across multiple line items in the same order.
**What it means:** the real unique identifier is the *combination* of 
(order_id, order_item_id) together, not either column alone.
**How to test it:** dbt's built-in `unique` test only checks one column. 
Testing a combination needs a generic `assert_stg_order_items_unique_grain` test.
**Where else this matters:** any table where "one row per X" isn't true — 
watch for this whenever a table represents line items, events, or anything 
that can repeat per parent record.

## 08/23/2026 - Singular Tests vs Generic Tests
**What I hit:** Can't test singular tests like combination, need to use SQL queries under tests.
**What it means:** Generic tests can be done under schema.yml with commands, but singular tests require a SQL freedom. 

# 08/24/2026 - Entry — Trend Window Sizing
What I hit: I needed to decide how many days count as "recent" vs. "prior" when checking if a seller's ordering is declining — a specific number, with no formula to just look up.

What it means: picking a window is a tradeoff, not a calculation. Too short, and normal random gaps between orders get mistaken for a real decline — a healthy seller can easily have zero orders in a short window just by chance. Too long, and you catch real declines too late to act on them, or lose the ability to call anything "recent" at all.

How I resolved it: I already knew the typical seller's real order cadence (median ~6.5 days, computed correctly at the per-seller level — see the earlier grain/aggregation lesson). I used that as a ruler: a window of roughly 4-6x that typical gap (~30-45 days) is long enough that a healthy seller would normally place several orders inside it, so an empty stretch that long is much more likely to be a real signal than noise — while still being short enough to count as "recent."

Where else this matters: any time I need to define a "look-back window" for detecting a change in behavior (declining engagement, slowing usage, dropping activity) — anchor the window size to the entity's own normal behavior/cadence, don't pick a round number out of habit. Be ready to explain the tradeoff (false alarms vs. catching it late), not just state the number.


