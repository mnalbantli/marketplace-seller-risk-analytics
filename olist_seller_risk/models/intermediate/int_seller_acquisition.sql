WITH closed_deals AS (
    SELECT
        mql_id,
        seller_id
    FROM {{ ref('stg_closed_deals') }}
),

qualified_leads AS (
    SELECT
        mql_id,
        origin
    FROM {{ ref('stg_qualified_leads') }}
)

SELECT
    cd.seller_id,
    ql.origin
FROM closed_deals cd
INNER JOIN qualified_leads ql ON cd.mql_id = ql.mql_id
