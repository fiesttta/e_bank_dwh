import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta

# --- НАСТРОЙКИ ПОДКЛЮЧЕНИЯ ---
DB_NAME = "e_bank"
DB_USER = "postgres" 
DB_PASS = "fiestta"
DB_HOST = "localhost"

fake = Faker('ru_RU')

def generate_bank_data():
    print("Подключаемся к базе данных...")
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cur = conn.cursor()

        # --- ОЧИСТКА СТАРЫХ ДАННЫХ ---
        print("Очищаем старые данные (TRUNCATE CASCADE)...")
        cur.execute("TRUNCATE TABLE transactions, accounts, clients, branches, products, currency_rates RESTART IDENTITY CASCADE;")

        # 1. Филиалы
        print("Строим филиалы...")
        branch_ids = []
        for _ in range(5):
            cur.execute("INSERT INTO branches (city, address, branch_type) VALUES (%s, %s, %s) RETURNING branch_id;",
                        (fake.city(), fake.street_address(), random.choice(['Physical', 'Digital'])))
            branch_ids.append(cur.fetchone()[0])

        # 2. Продукты
        print("Выпускаем продукты...")
        product_ids = []
        products = [('Classic Debit', 0.0), ('Gold Credit', 19.9), ('Premium Multi', 5.0), ('Savings', 12.5)]
        for p_name, p_rate in products:
            cur.execute("INSERT INTO products (product_name, interest_rate) VALUES (%s, %s) RETURNING product_id;",
                        (p_name, p_rate))
            product_ids.append(cur.fetchone()[0])

        # 3. Клиенты (Рандомные даты регистрации за последние 5 лет)
        print("Привлекаем 200 клиентов...")
        client_ids = []
        for _ in range(200):
            gender = random.choice(['M', 'F'])
            full_name = fake.name_male() if gender == 'M' else fake.name_female()
            reg_date = fake.date_between(start_date='-5y', end_date='today')
            
            cur.execute("INSERT INTO clients (full_name, email, gender, birth_date, registration_date) VALUES (%s, %s, %s, %s, %s) RETURNING client_id;",
                        (full_name, fake.unique.email(), gender, fake.date_of_birth(minimum_age=18, maximum_age=80), reg_date))
            client_ids.append(cur.fetchone()[0])

        # 4. Счета (Мультивалютность и даты открытия)
        print("Открываем счета...")
        account_data = {} # Сохраним инфу о счетах для транзакций (id: {currency, opened_at})
        for client_id in client_ids:
            for _ in range(random.randint(1, 4)):
                currency = random.choices(['RUB', 'USD', 'EUR'], weights=[80, 10, 10])[0]
                opened_at = fake.date_between(start_date='-4y', end_date='today')
                
                cur.execute("""INSERT INTO accounts (client_id, product_id, branch_id, account_number, balance, currency, opened_at) 
                               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING account_id;""",
                            (client_id, random.choice(product_ids), random.choice(branch_ids), 
                             fake.unique.bban(), round(random.uniform(0.0, 1000000.0), 2), currency, opened_at))
                acc_id = cur.fetchone()[0]
                account_data[acc_id] = {'currency': currency, 'opened_at': opened_at}

        # 5. Транзакции (С учетом дат регистрации + наличные)
        print("💸 Симулируем 5000 транзакций...")
        account_ids = list(account_data.keys())
        
        for _ in range(5000):
            # 1. Выбираем тип операции
            tx_type = random.choices(['transfer', 'salary', 'payment', 'cash_withdrawal', 'cash_deposit'], weights=[50, 10, 20, 10, 10])[0]
            amount = round(random.uniform(10.0, 50000.0), 2)
            
            acc_from = None
            acc_to = None
            acc_opened_date = None

            # 2. Логика распределения счетов в зависимости от типа
            if tx_type == 'cash_deposit': # Внесение наличных
                acc_to = random.choice(account_ids)
                acc_opened_date = account_data[acc_to]['opened_at']
                
            elif tx_type == 'cash_withdrawal': # Снятие наличных
                acc_from = random.choice(account_ids)
                acc_opened_date = account_data[acc_from]['opened_at']
                
            else: # transfer, salary, payment (между двумя счетами)
                acc_from = random.choice(account_ids)
                acc_to = random.choice(account_ids)
                while acc_from == acc_to:
                    acc_to = random.choice(account_ids)
                # Берем максимальную дату открытия из двух счетов! 
                # (чтобы не перевести деньги на счет, который еще не существует)
                acc_opened_date = max(account_data[acc_from]['opened_at'], account_data[acc_to]['opened_at'])
            
            # 3. Генерируем дату строго после открытия счетов
            tx_date = fake.date_time_between_dates(datetime_start=acc_opened_date, datetime_end=datetime.now())
            
            # 4. Отправляем в базу (None автоматически превратится в NULL)
            cur.execute("""INSERT INTO transactions (from_account_id, to_account_id, amount, tx_type, created_at) 
                           VALUES (%s, %s, %s, %s, %s);""",
                        (acc_from, acc_to, amount, tx_type, tx_date))

        # 6. Курсы валют (Исторические данные за год)
        print("Загружаем курсы валют...")
        base_date = datetime.now() - timedelta(days=365)
        for i in range(365):
            current_date = base_date + timedelta(days=i)
            # Немного волатильности для реализма
            usd_rate = round(random.uniform(85.0, 100.0), 4)
            eur_rate = round(usd_rate * random.uniform(1.05, 1.15), 4)
            
            cur.execute("INSERT INTO currency_rates (currency_code, rate_to_rub, effective_date) VALUES ('USD', %s, %s), ('EUR', %s, %s);",
                        (usd_rate, current_date, eur_rate, current_date))

        conn.commit()
        cur.close()
        conn.close()
        print("Успех! База e_bank заполнена элитными мок-данными.")

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    generate_bank_data()