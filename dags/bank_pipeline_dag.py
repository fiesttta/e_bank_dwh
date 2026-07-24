from datetime import datetime, timedelta
from socket import timeout
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.sensors.filesystem import FileSensor

from data_generator import generate_bank_data
from etl_pipeline import run_etl
from dq_checks import run_dq_checks
from fetch_rates import fetch_and_save_rates
from pg_to_gp_transfer import transfer_data_to_dwh

# заглушки типо уведомления
def send_success_notification():
    print("||| Успех. Витрины обновлены, данные в порядке |||")

def send_alarm_notification(**kwargs):
    errors = kwargs['ti'].xcom_pull(task_ids='run_dq_checks', key='dq_errors')
    print("||| В данных найдены ошибки |||")
    print(f"Подробности: {errors}")


default_args = {
    'owner': 'fiestta',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(seconds=10),
}

with DAG(
    dag_id='e_bank_daily_etl',
    default_args=default_args,
    description='Ежедневная загрузка и проверка данных банка',
    schedule_interval='0 2 * * *',
    catchup=False,
    tags=['e-bank', 'etl', 'dq'],
) as dag:

    wait_file_task = FileSensor(
        task_id='wait_trigger_file',
        filepath='/opt/airflow/etl/trigger.txt',
        poke_interval=23,
        mode='reschedule',
        timeout=60 * 60
    )

    generate_data_task = PythonOperator(
        task_id='generate_raw_data',
        python_callable=generate_bank_data,
    )

    run_etl_task = PythonOperator(
        task_id='run_etl_pipeline',
        python_callable=run_etl,
    )

    run_dq_branch = BranchPythonOperator(
        task_id='run_dq_checks',
        python_callable=run_dq_checks,
    )
    
    success_task = PythonOperator(
        task_id='dq_success_task',
        python_callable=send_success_notification
    )

    alarm_task = PythonOperator(
    task_id='dq_alarm_task',
    python_callable=send_alarm_notification
    )

    fetch_rates_task = PythonOperator(
        task_id='fetch_rates',
        python_callable=fetch_and_save_rates,
    )

    transfer_to_gp_task = PythonOperator(
        task_id='transfer_pg_to_gp',
        python_callable=transfer_data_to_dwh,
    )

    wait_file_task >> [generate_data_task, fetch_rates_task] 
    [generate_data_task, fetch_rates_task] >> transfer_to_gp_task
    transfer_to_gp_task >>  run_etl_task >> run_dq_branch >> [success_task, alarm_task]