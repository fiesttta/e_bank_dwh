from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'fiestta',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
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

    generate_data = BashOperator(
        task_id='generate_raw_data',
        bash_command='python /opt/airflow/etl/data_generator.py',
    )

    run_etl = BashOperator(
        task_id='run_etl_pipeline',
        bash_command='python /opt/airflow/etl/etl_pipeline.py',
    )

    run_dq = BashOperator(
        task_id='run_dq_checks',
        bash_command='python /opt/airflow/etl/dq_checks.py',
    )

    generate_data >> run_etl >> run_dq