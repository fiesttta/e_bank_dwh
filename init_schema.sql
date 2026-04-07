-- 1. Справочник филиалов
CREATE TABLE branches (
    branch_id SERIAL PRIMARY KEY,
    city TEXT NOT NULL,
    address TEXT,
    branch_type TEXT -- 'Physical', 'Digital'
);

-- 2. Справочник банковских продуктов
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name TEXT NOT NULL, -- 'Classic Debit', 'Gold Credit', 'Savings'
    interest_rate DECIMAL(5, 2) DEFAULT 0.00 -- Процентная ставка
);

-- 3. Клиенты
CREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE,
    gender CHAR(1),
    birth_date DATE,
    registration_date DATE DEFAULT CURRENT_DATE
);

-- 4. Счета
CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(client_id),
    product_id INTEGER REFERENCES products(product_id),
    branch_id INTEGER REFERENCES branches(branch_id),
    account_number VARCHAR(20) UNIQUE NOT NULL,
    balance DECIMAL(15, 2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'RUB',
    opened_at DATE DEFAULT CURRENT_DATE
);

-- 5. Транзакции
CREATE TABLE transactions (
    tx_id SERIAL PRIMARY KEY,
    from_account_id INTEGER REFERENCES accounts(account_id),
    to_account_id INTEGER REFERENCES accounts(account_id),
    amount DECIMAL(15, 2) NOT NULL,
    tx_type TEXT, -- 'transfer', 'withdrawal', 'deposit', 'fee'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Курсы валют
CREATE TABLE currency_rates (
    rate_id SERIAL PRIMARY KEY,
    currency_code VARCHAR(3),
    rate_to_rub DECIMAL(10, 4),
    effective_date DATE DEFAULT CURRENT_DATE
);