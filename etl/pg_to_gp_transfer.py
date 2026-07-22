import psycopg2
from psycopg2.extras import execute_values
from airflow.providers.postgres.hooks.postgres import PostgresHook

def transfer_data_to_dwh():
    print("/// Старт пререноса (new) ///")

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

        def load_table_in_chunks(table_name, chunk_size=10000):
            print(f"/// Перенос таблицы: {table_name.upper()} ///")

            if table_name == 'transactions':
                pg_cur.execute(f"SELECT * FROM {table_name} ORDER BY created_at;")
            else:
                pg_cur.execute(f"SELECT * FROM {table_name};")
            columns = [desc[0] for desc in pg_cur.description]
            col_names = ", ".join(columns)

            insert_query = f"INSERT INTO {table_name} ({col_names}) VALUES %s"

            rows_inserted = 0
            while True:
                records = pg_cur.fetchmany(chunk_size)

                if not records:
                    break

                execute_values(gp_cur, insert_query, records)
                gp_conn.commit()

                rows_inserted += len(records)
                print(f"/// Загружено {rows_inserted} строк... ///")
            print(f"Таблица {table_name} успешно перенесена. Строк: {rows_inserted}")

        for t in tables_to_load:
            load_table_in_chunks(t)
            
        pg_cur.close()
        gp_cur.close()
        pg_conn.close()
        gp_conn.close()

        print("/// Все перенесено успешно. ///")

    except Exception as e:
        print(f"Ошибка при переносе: {e}")

if __name__ == "__main__":
    transfer_data_to_dwh()