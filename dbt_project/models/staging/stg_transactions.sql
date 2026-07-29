SELECT
    tx_id,
    from_account_id,
    to_account_id,
    amount,
    tx_type,
    created_at,
    created_at::date AS tx_date
FROM {{ source('raw_bank', 'transactions') }}