-- stg_order_items grain is (order_id, order_item_id); fails if any combination repeats.
SELECT
    order_id,
    order_item_id,
    count(*) AS row_count
FROM {{ ref('stg_order_items') }}
GROUP BY order_id, order_item_id
HAVING count(*) > 1
