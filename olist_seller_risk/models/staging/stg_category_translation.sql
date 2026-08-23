WITH category_translation_raw AS (
    SELECT
        product_category_name AS category_name,
        product_category_name_english AS category_name_english
        -- renamed to align join key with stg_products (USING(category_name)).
    FROM {{ ref('product_category_translation') }}
)

SELECT * FROM category_translation_raw
