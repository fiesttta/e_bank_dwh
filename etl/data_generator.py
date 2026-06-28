import psycopg2
from psycopg2.extras import execute_values
from faker import Faker
import random
from datetime import datetime, timedelta
from airflow.providers.postgres.hooks.postgres import PostgresHook

fake = Faker('ru_RU')

def generate_bank_data():
    print("/// Подключаемся к базе данных... ///")
    try:
        hook = PostgresHook(postgres_conn_id="e_bank_conn")
        conn = hook.get_conn()
        cur = conn.cursor()

        print("/// Проверяем и создаем структуру таблиц... ///")
        cur.execute("""
            -- 1. Справочник филиалов
            CREATE TABLE IF NOT EXISTS branches (
                branch_id SERIAL PRIMARY KEY,
                city TEXT NOT NULL,
                address TEXT,
                branch_type TEXT -- 'Physical', 'Digital'
            );

            -- 2. Справочник банковских продуктов
            CREATE TABLE IF NOT EXISTS products (
                product_id SERIAL PRIMARY KEY,
                product_name TEXT NOT NULL,
                interest_rate DECIMAL(5, 2) DEFAULT 0.00
            );

            -- 3. Клиенты
            CREATE TABLE IF NOT EXISTS clients (
                client_id SERIAL PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE,
                gender CHAR(1),
                birth_date DATE,
                registration_date DATE DEFAULT CURRENT_DATE
            );

            -- 4. Счета
            CREATE TABLE IF NOT EXISTS accounts (
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
            CREATE TABLE IF NOT EXISTS transactions (
                tx_id SERIAL PRIMARY KEY,
                from_account_id INTEGER REFERENCES accounts(account_id),
                to_account_id INTEGER REFERENCES accounts(account_id),
                amount DECIMAL(15, 2) NOT NULL,
                tx_type TEXT, -- 'transfer', 'withdrawal', 'deposit', 'fee'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- 6. Курсы валют
            CREATE TABLE IF NOT EXISTS currency_rates (
                rate_id SERIAL PRIMARY KEY,
                currency_code VARCHAR(3),
                rate_to_rub DECIMAL(10, 4),
                effective_date DATE DEFAULT CURRENT_DATE
            );
        """)
        conn.commit()

        print("/// Очищаем старые данные... ///")
        cur.execute("TRUNCATE TABLE transactions, accounts, clients, branches, products, currency_rates RESTART IDENTITY CASCADE;")

        print("/// Строим филиалы... ///")
        branch_ids = []
        for _ in range(10):
            cur.execute("INSERT INTO branches (city, address, branch_type) VALUES (%s, %s, %s) RETURNING branch_id;",
                        (fake.city(), fake.street_address(), random.choice(['Physical', 'Digital'])))
            branch_ids.append(cur.fetchone()[0])

        print("/// Выпускаем продукты... ///")
        product_ids = []
        products = [('Classic Debit', 0.0), ('Gold Credit', 19.9), ('Premium Multi', 5.0), ('Savings', 12.5), ('Crypto Card', 1.5)]
        for p_name, p_rate in products:
            cur.execute("INSERT INTO products (product_name, interest_rate) VALUES (%s, %s) RETURNING product_id;",
                        (p_name, p_rate))
            product_ids.append(cur.fetchone()[0])

        print("/// Привлекаем 3000 клиентов... ///")
        client_data_to_insert = []
        for _ in range(3000):
            gender = random.choice(['M', 'F'])
            full_name = fake.name_male() if gender == 'M' else fake.name_female()
            reg_date = fake.date_between(start_date='-5y', end_date='today')
            birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80)
            client_data_to_insert.append((full_name, fake.unique.email(), gender, birth_date, reg_date))
        
        execute_values(cur, "INSERT INTO clients (full_name, email, gender, birth_date, registration_date) VALUES %s", client_data_to_insert)

        cur.execute("SELECT client_id, registration_date FROM clients;")
        client_data = cur.fetchall()

        print("/// Открываем счета... ///")
        account_data_to_insert = []
        for client_id, reg_date in client_data:
            for _ in range(random.randint(1, 3)):
                currency = random.choices(['RUB', 'USD', 'EUR'], weights=[80, 10, 10])[0]
                opened_at = fake.date_between(start_date=reg_date, end_date='today')
                balance = round(random.uniform(0.0, 1000000.0), 2)
                account_data_to_insert.append((client_id, random.choice(product_ids), random.choice(branch_ids), fake.unique.bban(), balance, currency, opened_at))

        execute_values(cur, "INSERT INTO accounts (client_id, product_id, branch_id, account_number, balance, currency, opened_at) VALUES %s", account_data_to_insert)
        
        cur.execute("SELECT account_id, opened_at FROM accounts;")
        accounts_rows = cur.fetchall()
        account_ids = [row[0] for row in accounts_rows]
        account_dates = {row[0]: row[1] for row in accounts_rows}

        print("/// Симулируем 200000 транзакций... ///")
        tx_data_to_insert = []
        
        for _ in range(200000):
            tx_type = random.choices(['transfer', 'salary', 'payment', 'cash_withdrawal', 'cash_deposit'], weights=[50, 10, 20, 10, 10])[0]
            amount = round(random.uniform(10.0, 100000.0), 2)
            
            acc_from = None
            acc_to = None
            acc_opened_date = None

            if tx_type == 'cash_deposit':
                acc_to = random.choice(account_ids)
                acc_opened_date = account_dates[acc_to]
                
            elif tx_type == 'cash_withdrawal':
                acc_from = random.choice(account_ids)
                acc_opened_date = account_dates[acc_from]
                
            else:
                acc_from = random.choice(account_ids)
                acc_to = random.choice(account_ids)
                while acc_from == acc_to:
                    acc_to = random.choice(account_ids)
                acc_opened_date = max(account_dates[acc_from], account_dates[acc_to])
            
            tx_date = fake.date_time_between_dates(datetime_start=acc_opened_date, datetime_end=datetime.now())
            tx_data_to_insert.append((acc_from, acc_to, amount, tx_type, tx_date))

        # по 10000 что бы не сдох python
        batch_size = 10000
        for i in range(0, len(tx_data_to_insert), batch_size):
            batch = tx_data_to_insert[i:i+batch_size]
            execute_values(cur, "INSERT INTO transactions (from_account_id, to_account_id, amount, tx_type, created_at) VALUES %s", batch)
          
        print("/// Загружаем курсы валют... ///")
        years_5_in_days = 5 * 365
        base_date = datetime.now() - timedelta(days=years_5_in_days)
        rates_to_insert = []
        for i in range(years_5_in_days):
            current_date = base_date + timedelta(days=i)
            usd_rate = round(random.uniform(85.0, 100.0), 4)
            eur_rate = round(usd_rate * random.uniform(1.05, 1.15), 4)
            rates_to_insert.append(('USD', usd_rate, current_date))
            rates_to_insert.append(('EUR', eur_rate, current_date))
            
        execute_values(cur, "INSERT INTO currency_rates (currency_code, rate_to_rub, effective_date) VALUES %s", rates_to_insert)

        conn.commit()
        cur.close()
        conn.close()
        print("/// Успех! База заполнена мок-данными. ///")

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    generate_bank_data()