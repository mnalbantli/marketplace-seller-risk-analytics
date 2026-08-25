-- cancellation_rate and unresolved_rate must each fall in [0, 1]; fails if any row is out of bounds.
SELECT
    seller_id,
    cancellation_rate,
    unresolved_rate
FROM {{ ref('int_seller_order_activity') }}
WHERE cancellation_rate < 0 OR cancellation_rate > 1
   OR unresolved_rate < 0 OR unresolved_rate > 1
