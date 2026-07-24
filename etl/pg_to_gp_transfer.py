import psycopg2
import os
from airflow.providers.postgres.hooks.postgres import PostgresHook

def transfer_data_to_dwh():
    print("/// Старт пререноса (ыекуфь) ///")

    try:
        pg_hook = PostgresHook(postgres_conn_id="e_bank_conn")
        pg_conn = pg_hook.get_conn()
        pg_cur = pg_conn.cursor()

        gp_hook = PostgresHook(postgres_conn_id="greenplum_dwh")
        gp_conn = gp_hook.get_conn()
        gp_cur = gp_conn.cursor()

        print("/// Подключения установленны ///")

        tables_to_load = ['branches', 'products', 'currency_rates', 'clients', 'accounts', 'transactions']

        print("/// Предварительная очистка ///")
        for table in tables_to_load:
            gp_cur.execute(f"TRUNCATE TABLE {table};")
        gp_conn.commit()

        def stream_table(table_name):
            print(f"/// Перенос таблицы: {table_name.upper()} ///")

            tmp_file = f"/tmp/{table_name}.csv"

            print("/// Выгрузка в буфер ///")
            with open(tmp_file, 'w') as f:
                if table_name == 'transactions':
                    pg_cur.copy_expert(f"COPY (SELECT * FROM {table_name} ORDER BY created_at) TO STDOUT WITH CSV HEADER", f)
                else:
                    pg_cur.copy_expert(f"COPY {table_name} TO STDOUT WITH CSV HEADER", f)

            print("/// Поток в GP ///")
            with open(tmp_file, 'r') as f:
                gp_cur.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER", f)
            gp_conn.commit()

            if os.path.exists(tmp_file):
                os.remove(tmp_file)

            gp_cur.execute(f"SELECT COUNT(*) FROM {table_name};")
            rows_inserted = gp_cur.fetchone()[0]
            print(f"Успешно. Строк: {rows_inserted}\n")

        for t in tables_to_load:
            stream_table(t)
            
        pg_cur.close()
        gp_cur.close()
        pg_conn.close()
        gp_conn.close()

        print("/// Все перенесено успешно. ///")

    except Exception as e:
        print(f"Ошибка при переносе: {e}")
        raise e
    
if __name__ == "__main__":
    transfer_data_to_dwh()