SELECT
    account_id,
    currency
FROM {{ source('raw_bank', 'accounts') }}
