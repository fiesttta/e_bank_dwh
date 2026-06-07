"""Ежедневное удаление старых данных из XCom со всех DAG'ов. Очистка служебной БД."""

from airflow.models import DAG
from airflow.utils.db import provide_session
from airflow.models import XCom
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime
import logging

logger = logging.getLogger("airflow.task")

DEFAULT_ARGS = {
    "owner": "fiestta",
    "retries": 2,
    "retry_delay": 600,
    "start_date": datetime(2024, 1, 1),
}

with DAG(
    dag_id="TECH_Clean_Xcom",
    default_args=DEFAULT_ARGS,
    schedule_interval="@daily",
    description="Очистка мусора в XCom каждый день",
    tags=["clean_xcom", "maintenance", "e-bank"],
    catchup=False
) as dag:

    @provide_session
    def cleanup_xcom(session=None, **context):
        # Удаляем данные, которые хранятся более суток
        num_rows_deleted = 0
        date_limit = context["logical_date"]
        logger.info(f"Удаляем данные старше {date_limit}")
        
        try:
            num_rows_deleted = (
                session.query(XCom).filter(XCom.timestamp <= date_limit).delete()
            )
            session.commit()
        except Exception as e:
            logger.error(f"Ошибка при очистке БД: {e}")
            session.rollback()

        if num_rows_deleted == 0:
            logger.info("Нет старых записей для удаления.")
        else:
            logger.info(f"Успех! Удалено {num_rows_deleted} строк из XCom.")

    clean_xcom = PythonOperator(
        task_id="cleanup_xcom",
        python_callable=cleanup_xcom,
    )

    dag_start = EmptyOperator(task_id="start")
    dag_end = EmptyOperator(task_id="end", trigger_rule="none_failed")

    # Привязываем описание из начала файла в UI Airflow
    dag.doc_md = __doc__

    dag_start >> clean_xcom >> dag_end