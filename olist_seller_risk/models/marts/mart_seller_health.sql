WITH order_activity AS (
    SELECT
        seller_id,
        gmv,
        order_count,
        cancellation_rate,
        unresolved_rate,
        recency_days,
        trend_eligible,
        orders_last_30d,
        orders_prior_30d
    FROM {{ ref('int_seller_order_activity') }}
),

category_mix AS (
    SELECT
        seller_id,
        category_name,
        category_gmv_pct,
        -- alphabetical tie-break on category_name: deterministic/stable across
        -- runs only, carries no business meaning (3 sellers have an exact
        -- category_gmv tie as of 2026-08-25)
        ROW_NUMBER() OVER (
            PARTITION BY seller_id
            ORDER BY category_gmv DESC, category_name ASC
        ) AS category_rank
    FROM {{ ref('int_seller_category_mix') }}
),

top_category AS (
    SELECT
        seller_id,
        category_name AS top_category,
        category_gmv_pct AS category_concentration_pct
    FROM category_mix
    WHERE category_rank = 1
),

acquisition AS (
    SELECT
        seller_id,
        origin
    FROM {{ ref('int_seller_acquisition') }}
),

sellers AS (
    SELECT
        seller_id,
        seller_city,
        seller_state
    FROM {{ ref('stg_sellers') }}
)

SELECT
    oa.seller_id,
    oa.gmv,
    oa.order_count,
    oa.cancellation_rate,
    oa.unresolved_rate,
    oa.recency_days,
    oa.trend_eligible,
    oa.orders_last_30d,
    oa.orders_prior_30d,
    tc.top_category,
    tc.category_concentration_pct,
    acq.origin,
    s.seller_city,
    s.seller_state
FROM order_activity oa
LEFT JOIN top_category tc ON oa.seller_id = tc.seller_id
LEFT JOIN acquisition acq ON oa.seller_id = acq.seller_id
LEFT JOIN sellers s ON oa.seller_id = s.seller_id
