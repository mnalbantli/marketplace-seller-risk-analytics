-- int_seller_category_mix grain is (seller_id, category_name); fails if any combination repeats.
SELECT
    seller_id,
    category_name,
    count(*) AS row_count
FROM {{ ref('int_seller_category_mix') }}
GROUP BY seller_id, category_name
HAVING count(*) > 1
