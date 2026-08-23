WITH order_items_raw AS (
    SELECT
        order_id,
        order_item_id,
        product_id,
        seller_id,
        price,
        freight_value
        -- dropped shipping_limit_date (seller fulfillment deadline, not relevant to
        -- churn-risk/GMV) and the 8 product-attribute columns (product_category_name,
        -- product_name_lenght, product_description_lenght, product_photos_qty,
        -- product_weight_g, product_length_cm, product_height_cm, product_width_cm):
        -- all NULL on every real order row here — category comes from
        -- stg_products/stg_category_translation instead.
    FROM {{ source('raw', 'order_items') }}
    WHERE order_id IS NOT NULL
    -- drops ~32,951 phantom rows (one per distinct product_id) where order_id,
    -- order_item_id, seller_id, price, and freight_value are all NULL — a join/union
    -- artifact upstream in how this raw table was built, not real Olist data.
)

SELECT * FROM order_items_raw
