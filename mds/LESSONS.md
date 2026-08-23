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

