WITH order_items AS (
    SELECT
        order_id,
        seller_id,
        product_id,
        price
    FROM {{ ref('stg_order_items') }}
),

products AS (
    SELECT
        product_id,
        category_name
    FROM {{ ref('stg_products') }}
),

orders AS (
    SELECT
        order_id,
        order_status
    FROM {{ ref('stg_orders') }}
),

delivered_known_category AS (
    -- delivered-only (same GMV basis as int_seller_order_activity), and
    -- NULL-category items excluded entirely (~1.3% of marketplace GMV, see PROCESS.md)
    SELECT
        oi.seller_id,
        p.category_name,
        oi.price
    FROM order_items oi
    INNER JOIN products p ON oi.product_id = p.product_id
    INNER JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
        AND p.category_name IS NOT NULL
),

category_agg AS (
    SELECT
        seller_id,
        category_name,
        SUM(price) AS category_gmv
    FROM delivered_known_category
    GROUP BY seller_id, category_name
),

seller_totals AS (
    -- per-seller denominator: summed across only that seller's known-category rows above
    SELECT
        seller_id,
        SUM(category_gmv) AS seller_total_gmv
    FROM category_agg
    GROUP BY seller_id
)

SELECT
    ca.seller_id,
    ca.category_name,
    ca.category_gmv,
    ca.category_gmv / st.seller_total_gmv AS category_gmv_pct
FROM category_agg ca
INNER JOIN seller_totals st ON ca.seller_id = st.seller_id
