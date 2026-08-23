WITH orders_raw AS (
    SELECT
        order_id,
        order_purchase_timestamp,
        order_status,
        order_delivered_customer_date
    FROM {{ source('raw', 'orders') }}
)

SELECT * FROM orders_raw