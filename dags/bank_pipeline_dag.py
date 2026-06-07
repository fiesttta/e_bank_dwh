from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
# Наши функции
from data_generator import generate_bank_data
from etl_pipeline import run_etl
from dq_checks import run_dq_checks
from fetch_rates import fetch_and_save_rates

# заглушки типо уведомления
def send_success_notification():
    print("||| Успех. Витрины обновлены, данные в порядке |||")

def send_alarm_notification():
    errors = kwargs['ti'].xcom_pull(task_ids='run_dq_checks', key='dq_errors')
    print("||| В данных найдены ошибки |||")
    print(f"Подробности: {errors}")


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

    generate_data_task >> fetch_rates_task >> run_etl_task >> run_dq_branch 
    run_dq_branch >> [success_task, alarm_task]