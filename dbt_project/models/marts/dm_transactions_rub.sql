{{ config(
    materialized='table'
) }}

SELECT
    t.tx_id,
    t.created_at,
    t.tx_type,
    t.currency,
    t.amount AS original_amount,
    CASE
        WHEN t.currency = 'RUB' THEN t.amount
        ELSE ROUND(t.amount * COALESCE(cr.rate_to_rub, 90.0), 2)
    END AS amount_rub
FROM {{ ref('int_transactions_enriched') }} t
LEFT JOIN {{ ref('stg_currency_rates') }} cr
    ON t.currency = cr.currency_code
    AND t.tx_date = cr.effective_date