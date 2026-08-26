WITH closed_deals_raw AS (
    SELECT
        mql_id,
        seller_id
        -- dropped sdr_id, sr_id, won_date, business_segment, lead_type,
        -- lead_behaviour_profile, has_company, has_gtin, average_stock,
        -- business_type, declared_product_catalog_size, declared_monthly_revenue:
        -- no current analytical use (business_segment/lead_type reviewed and
        -- cut per PROCESS.md's driver-screening criteria)
    FROM {{ source('raw', 'closed_deals') }}
)

SELECT * FROM closed_deals_raw
