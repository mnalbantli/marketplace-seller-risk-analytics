SELECT
    seller_id,
    risk_score,
    gmv,
    gmv_at_risk_weighted
FROM {{ ref('seed_seller_risk_scores') }}
