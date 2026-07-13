import psycopg2
from airflow.providers.postgres.hooks.postgres import PostgresHook

def run_dq_checks(**kwargs):
    print("/// Начало проверки ///")

    hook = PostgresHook(postgres_conn_id="greenplum_dwh")
    conn = hook.get_conn()
    cur = conn.cursor()
    
    errors = []
    
    cur.execute("SELECT COUNT(*) FROM transactions WHERE amount <= 0;")
    invalid_tx_count = cur.fetchone()[0]
    if invalid_tx_count > 0:
        errors.append(f"Транзакций с суммой <= 0: {invalid_tx_count}")  

    cur.execute("SELECT COUNT(*) FROM clients WHERE email IS NULL OR email = '';")
    null_emails = cur.fetchone()[0]
    if null_emails > 0:
        errors.append(f"Клиентов без email: {null_emails}")

    cur.execute("SELECT COUNT(*) FROM accounts WHERE balance IS NULL;")
    null_balance = cur.fetchone()[0]
    if null_balance > 0:
        errors.append(f"Счетов с NULL балансом: {null_balance}")

    cur.close()
    conn.close()

    if len(errors) > 0:
        error_message = " | ".join(errors)
        kwargs['ti'].xcom_push(key='dq_errors', value=error_message)
        print("/// Найдены ошибки, рычаг на ALARM ветку ///")
        return 'dq_alarm_task'
    else:
        print("/// Данные чисты и готовы к обработке ///")
        return 'dq_success_task'