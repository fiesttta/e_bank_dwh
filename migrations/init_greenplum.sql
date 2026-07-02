CREATE TABLE IF NOT EXISTS branches (
    branch_id INTEGER,
    city TEXT,
    address TEXT,
    branch_type TEXT
)
WITH (appendoptimized=true, orientation=column)
DISTRIBUTED REPLICATED;

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER,
    product_name TEXT,
    interest_rate DECIMAL(5, 2)
)
WITH (appendoptimized=true, orientation=column)
DISTRIBUTED REPLICATED;

CREATE TABLE IF NOT EXISTS currency_rates (
    rate_id INTEGER,
    currency_code VARCHAR(3),
    rate_to_rub DECIMAL(10, 4),
    effective_date DATE
) 
WITH (appendoptimized=true, orientation=column)
DISTRIBUTED REPLICATED;

CREATE TABLE IF NOT EXISTS clients (
    client_id INTEGER,
    full_name TEXT,
    email TEXT,
    gender CHAR(1),
    birth_date DATE,
    registration_date DATE
) 
WITH (appendoptimized=true, orientation=column)
DISTRIBUTED BY (client_id);

CREATE TABLE IF NOT EXISTS accounts (
    account_id INTEGER,
    client_id INTEGER,
    product_id INTEGER,
    branch_id INTEGER,
    account_number VARCHAR(20),
    balance DECIMAL(15, 2),
    currency VARCHAR(3),
    opened_at DATE
) 
WITH (appendoptimized=true, orientation=column)
DISTRIBUTED BY (account_id);

CREATE TABLE IF NOT EXISTS transactions (
    tx_id INTEGER,
    from_account_id INTEGER,
    to_account_id INTEGER,
    amount DECIMAL(15, 2),
    tx_type TEXT,
    created_at TIMESTAMP
) 
WITH (appendoptimized=true, orientation=column)
DISTRIBUTED BY (from_account_id);
