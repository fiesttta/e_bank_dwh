import psycopg2
import sys

DB_NAME = "e_bank"
DB_USER = "postgres"
DB_PASS = "fiestta"
DB_HOST = "db"

def run_dq_checks():
    print("Начало проверки.")
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cur = conn.cursor()

        
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