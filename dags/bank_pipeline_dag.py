from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
# импортируем питоновский оператор
from airflow.operators.python import PythonOperator
# Наши функции
from data_generator import generate_bank_data
from etl_pipeline import run_etl
from dq_checks import run_dq_checks


default_args = {
    'owner': 'fiestta',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='e_bank_daily_etl',
    default_args=default_args,
    description='Ежедневная загрузка и проверка данных банка',
    schedule_interval='0 2 * * *',
    catchup=False,
    tags=['e-bank', 'etl', 'dq'],
) as dag:
    # пока меняем только тут на питон оп
    generate_data_task = PythonOperator(
        task_id='generate_raw_data',
        python_callable=generate_bank_data,
    )

    run_etl_task = PythonOperator(
        task_id='run_etl_pipeline',
        python_callable=run_etl,
    )

    run_dq_task = PythonOperator(
        task_id='run_dq_checks',
        python_callable=run_dq_checks,
    )

    generate_data_task >> run_etl_task >> run_dq_task