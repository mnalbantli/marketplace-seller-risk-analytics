-- category_gmv_pct must fall in [0, 1]; fails if any row is out of bounds.
SELECT
    seller_id,
    category_name,
    category_gmv_pct
FROM {{ ref('int_seller_category_mix') }}
WHERE category_gmv_pct < 0 OR category_gmv_pct > 1
