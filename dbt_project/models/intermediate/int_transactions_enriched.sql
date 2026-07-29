SELECT
    t.tx_id,
    t.created_at,
    t.tx_date,
    t.tx_type,
    t.amount,
    COALESCE(a_from.currency, a_to.currency) AS currency
FROM {{ ref('stg_transactions') }} t
LEFT JOIN {{ ref('stg_accounts') }} a_from
    ON t.from_account_id = a_from.account_id
LEFT JOIN {{ ref('stg_accounts') }} a_to
    ON t.to_account_id = a_to.account_id
    