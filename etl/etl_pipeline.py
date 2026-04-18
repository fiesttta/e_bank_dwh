"""
Данный код это классический ETL-скрипт.
Задача стоит в том что бы создать витрину данных с конвертацией 
валюты на момент совершения транзакции.
"""

import psycopg2
from psycopg2.extras import execute_values
from datetime import date

# Переменные для подключения
DB_NAME = "e_bank"
DB_USER = "postgres"
DB_PASS = "fiestta"
DB_HOST = "db"

# Создание функции для нашего ETL процесса
def run_etl():
    print("Старт ETL-процесса...")
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cur = conn.cursor()

        # Подготовка витрины
        print("Создание таблицы-витрины dm_transactions_rub...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS dm_transactions_rub (
                    tx_id INTEGER PRIMARY KEY,
                    created_at TIMESTAMP,
                    tx_type TEXT,
                    currency VARCHAR(3),
                    original_amount DECIMAL(15, 2),
                    amount_rub DECIMAL(15, 2)
                );
                TRUNCATE TABLE dm_transactions_rub;
        """)

        # EXTRACT (Извлечение ланных)
        print("Извлечение данных [EXTRACT]")
        # Вытаскивание транзакций и определение их валюты (если from_account NULL, берем to_account)
        cur.execute("""
            SELECT
                t.tx_id, t.created_at, t.tx_type, t.amount,
                COALESCE(a_from.currency, a_to.currency) AS currency
                FROM transactions t
                LEFT JOIN accounts a_from ON t.from_account_id = a_from.account_id
                LEFT JOIN accounts a_to ON t.to_account_id = a_to.account_id;
        """)
        raw_transactions = cur.fetchall()

        # Вытаскивание курса валют по датам и помещение их в словарь python
        cur.execute("SELECT currency_code, effective_date, rate_to_rub FROM currency_rates;")
        rates_dict = {(row[0], row[1]): float(row[2]) for row in cur.fetchall()}

        # TRANSFORM (Трансформация данных в Python)
        print("Трансформация данных (Конвертирование в рубли)...")
        transformed_data = []

        for tx in raw_transactions:
            tx_id, created_at, tx_type, amount, currency = tx
            tx_date = created_at.date()
            amount = float(amount)

            if currency == 'RUB':
                amount_rub = amount
            else:
                # Поиск курса на день транзакции. Если нет, ставится средний 90 руб.
                rate = rates_dict.get((currency, tx_date), 90.0)
                amount_rub = round(amount * rate, 2)

            # Сборка очищенной строки для витрины
            transformed_data.append((tx_id, created_at, tx_type, currency, amount, amount_rub))

        # LOAD (Загрузка в витрину)
        print(f"Загрузка {len(transformed_data)} строк в витрину...")
        insert_query = """
            INSERT INTO dm_transactions_rub (tx_id, created_at, tx_type, currency, original_amount, amount_rub)
            VALUES %s
        """

        # Вставка сразу всех строк
        execute_values(cur, insert_query, transformed_data)

        conn.commit()
        cur.close()
        conn.close()
        print("Успех! ETL-процесс завершен.")

    except Exception as e:
        print(f"Ошибка: {e}")

# Запуск только из под терминала
if __name__ == "__main__":
    run_etl()