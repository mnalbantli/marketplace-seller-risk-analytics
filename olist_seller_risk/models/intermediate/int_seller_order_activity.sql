WITH order_items AS (
    SELECT
        order_id,
        seller_id,
        price
    FROM {{ ref('stg_order_items') }}
),

orders AS (
    SELECT
        order_id,
        order_status,
        order_purchase_timestamp
    FROM {{ ref('stg_orders') }}
),

reference_date AS (
    -- computed once across the whole dataset, reused for recency and the 30d windows
    SELECT MAX(order_purchase_timestamp) AS reference_date
    FROM orders
),

order_activity AS (
    SELECT
        oi.seller_id,
        o.order_id,
        o.order_purchase_timestamp,
        oi.price,
        CASE
            WHEN o.order_status = 'delivered' THEN 'delivered'
            WHEN o.order_status IN ('canceled', 'unavailable') THEN 'cancelled_unavailable'
            ELSE 'unresolved_unknown'
        END AS status_bucket
    FROM order_items oi
    INNER JOIN orders o ON oi.order_id = o.order_id
),

seller_agg AS (
    SELECT
        oa.seller_id,
        SUM(CASE WHEN oa.status_bucket = 'delivered' THEN oa.price ELSE 0 END) AS gmv,
        COUNT(DISTINCT CASE WHEN oa.status_bucket = 'delivered' THEN oa.order_id END) AS order_count,
        COUNT(DISTINCT oa.order_id) AS total_order_count,
        COUNT(DISTINCT CASE WHEN oa.status_bucket = 'cancelled_unavailable' THEN oa.order_id END) AS cancelled_unavailable_count,
        COUNT(DISTINCT CASE WHEN oa.status_bucket = 'unresolved_unknown' THEN oa.order_id END) AS unresolved_unknown_count,
        MAX(CASE WHEN oa.status_bucket = 'delivered' THEN oa.order_purchase_timestamp END) AS last_order_date,
        -- last 30 days: (reference_date - 30d, reference_date]
        COUNT(DISTINCT CASE
            WHEN oa.status_bucket = 'delivered'
                AND oa.order_purchase_timestamp > DATE_SUB(rd.reference_date, 30)
                AND oa.order_purchase_timestamp <= rd.reference_date
            THEN oa.order_id
        END) AS orders_last_30d_raw,
        -- prior 30 days: (reference_date - 60d, reference_date - 30d]
        COUNT(DISTINCT CASE
            WHEN oa.status_bucket = 'delivered'
                AND oa.order_purchase_timestamp > DATE_SUB(rd.reference_date, 60)
                AND oa.order_purchase_timestamp <= DATE_SUB(rd.reference_date, 30)
            THEN oa.order_id
        END) AS orders_prior_30d_raw
    FROM order_activity oa
    CROSS JOIN reference_date rd
    GROUP BY oa.seller_id
)

SELECT
    sa.seller_id,
    sa.gmv,
    sa.order_count,
    sa.cancelled_unavailable_count / sa.total_order_count AS cancellation_rate,
    sa.unresolved_unknown_count / sa.total_order_count AS unresolved_rate,
    DATEDIFF(rd.reference_date, sa.last_order_date) AS recency_days,
    sa.order_count >= 4 AS trend_eligible,
    CASE WHEN sa.order_count >= 4 THEN sa.orders_last_30d_raw END AS orders_last_30d,
    CASE WHEN sa.order_count >= 4 THEN sa.orders_prior_30d_raw END AS orders_prior_30d
FROM seller_agg sa
CROSS JOIN reference_date rd
