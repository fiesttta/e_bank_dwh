import psycopg2
import sys
# импорт хука для подключения
from airflow.providers.postgres.hooks.postgres import PostgresHook

def run_dq_checks():
    print("Начало проверки.")
    try:
        # подключаемся с помощью хука
        hook = PostgresHook(postgres_conn_id="e_bank_conn")
        conn = hook.get_conn()
        cur = conn.cursor()
        print("Подключение к БД установлено.")
        
        cur.execute("SELECT COUNT(*) FROM transactions WHERE amount <= 0;")
        invalid_tx_count = cur.fetchone()[0]

        if invalid_tx_count > 0:
            raise ValueError(f"Найдено {invalid_tx_count} транзакций с нулевой/отрицательной суммой")
        print("Проерка пройдена. 1/3")   

        cur.execute("SELECT COUNT(*) FROM clients WHERE email IS NULL OR email = '';")
        null_emails = cur.fetchone()[0]

        if null_emails > 0:
            raise ValueError(f"Найдено {null_emails} клиентов без email")
        print("Проверка пройдена. 2/3")

        cur.execute("SELECT COUNT(*) FROM accounts WHERE balance IS NULL;")
        null_balance = cur.fetchone()[0]

        if null_balance > 0:
            raise ValueError(f"Найдено {null_balance} счетов со значением баланса NULL")
        print("Проверка пройдена 3/3")

        print("Данные чисты и готовы к дальнейшей работе.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Не удалось запустить проверку: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_dq_checks()