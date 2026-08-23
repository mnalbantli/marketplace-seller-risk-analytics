WITH products_raw AS (
    SELECT
        product_id,
        -- dropped product_name_lenght, product_description_lenght, product_photos_qty,
        -- product_weight_g, product_length_cm, product_height_cm, product_width_cm:
        -- physical/listing attributes, don't answer the seller-risk business question
        product_category_name AS category_name
        -- renamed to align join key with stg_category_translation (USING(category_name)).
        -- NULL for 610 rows, left as-is (no imputation). order_items cannot backfill
        -- this (category is NULL on every real order row there) — products is the
        -- only source, so NULL here means NULL everywhere downstream unless handled
        -- explicitly in intermediate.
    FROM {{ source('raw', 'products') }}
)

SELECT * FROM products_raw
