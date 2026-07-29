SELECT
    currency_code,
    effective_date,
    rate_to_rub
FROM {{source('raw_bank', 'currency_rates') }}
