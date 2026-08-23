WITH sellers_raw AS (
    SELECT
        seller_id,
        -- dropped zip_code
        seller_city,
        seller_state
    FROM {{ source('raw', 'sellers') }}
)

SELECT * FROM sellers_raw