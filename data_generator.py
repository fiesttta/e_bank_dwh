import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta

# --- НАСТРОЙКИ ПОДКЛЮЧЕНИЯ ---
DB_NAME = "e_bank"
DB_USER = "postgres" 
DB_PASS = "fiestta"
DB_HOST = "localhost"

# Инициализируем Faker для генерации русских имен и адресов
fake = Faker('ru_RU')

def generate_bank_data():
    print("Подключаемся к базе данных...")
    try:
        # Подключаемся к PostgreSQL
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cur = conn.cursor()

        # 1. Генерируем филиалы (5 штук)
        print("Строим филиалы...")
        branch_ids = []
        for _ in range(5):
            cur.execute(
                "INSERT INTO branches (city, address, branch_type) VALUES (%s, %s, %s) RETURNING branch_id;",
                (fake.city(), fake.street_address(), random.choice(['Physical', 'Digital']))
            )
            branch_ids.append(cur.fetchone()[0])

        # 2. Генерируем продукты (3 штуки)
        print("Выпускаем банковские продукты...")
        product_ids = []
        products = [('Classic Debit', 0.0), ('Gold Credit', 19.9), ('Savings', 8.5)]
        for p_name, p_rate in products:
            cur.execute(
                "INSERT INTO products (product_name, interest_rate) VALUES (%s, %s) RETURNING product_id;",
                (p_name, p_rate)
            )
            product_ids.append(cur.fetchone()[0])

        # 3. Генерируем клиентов (100 человек)
        print("Привлекаем клиентов...")
        client_ids = []
        for _ in range(100):
            gender = random.choice(['M', 'F'])
            # Faker умеет генерировать ФИО с учетом пола
            full_name = fake.name_male() if gender == 'M' else fake.name_female() 
            
            cur.execute(
                "INSERT INTO clients (full_name, email, gender, birth_date) VALUES (%s, %s, %s, %s) RETURNING client_id;",
                (full_name, fake.unique.email(), gender, fake.date_of_birth(minimum_age=18, maximum_age=80))
            )
            client_ids.append(cur.fetchone()[0])

        # 4. Открываем счета для клиентов (около 150 счетов)
        print("Открываем счета...")
        account_ids = []
        for client_id in client_ids:
            # У одного клиента может быть от 1 до 3 счетов
            for _ in range(random.randint(1, 3)):
                cur.execute(
                    """INSERT INTO accounts (client_id, product_id, branch_id, account_number, balance) 
                       VALUES (%s, %s, %s, %s, %s) RETURNING account_id;""",
                    (client_id, random.choice(product_ids), random.choice(branch_ids), 
                     fake.unique.bban(), round(random.uniform(100.0, 500000.0), 2))
                )
                account_ids.append(cur.fetchone()[0])

        # 5. Генерируем транзакции (2000 переводов)
        print("Симулируем транзакции...")
        for _ in range(2000):
            acc_from = random.choice(account_ids)
            acc_to = random.choice(account_ids)
            while acc_from == acc_to: # Чтобы не переводили сами себе
                acc_to = random.choice(account_ids)
            
            amount = round(random.uniform(50.0, 15000.0), 2)
            
            cur.execute(
                """INSERT INTO transactions (from_account_id, to_account_id, amount, tx_type) 
                   VALUES (%s, %s, %s, %s);""",
                (acc_from, acc_to, amount, 'transfer')
            )

        # Сохраняем все изменения в базу
        conn.commit()
        cur.close()
        conn.close()
        print("Успех! База данных заполнена.")

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    generate_bank_data()