WITH qualified_leads_raw AS (
    SELECT
        mql_id,
        origin
        -- dropped first_contact_date and landing_page_id: no current analytical use
    FROM {{ source('raw', 'qualified_leads') }}
)

SELECT * FROM qualified_leads_raw
