# 🏦 E-Bank DWH & ELT Pipeline (Dockerized)

Это мой пет проект, в котором я с нуля спроектировал и построил аналитическое хранилище данных (DWH) для выдуманного цифрового банка. 

Проект прошел путь от простых SQL-запросов и ETL до **умного докеризированного ELT-пайплайна**, который управляется оркестратором, использует колоночное MPP-хранилище (Greenplum), общается со сторонними API и автоматически проверяет качество данных.

## 📊 Результат работы (BI Dashboard в Metabase)
![E-Bank Dashboard](dashboard.png)

## 🛠 Что внутри? (Стек)
* **Инфраструктура:** Docker, Docker Compose, Bash-скрипт автоматизации (`start.sh`).
* **Оркестрация (Apache Airflow):** BranchPythonOperator, FileSensor, XCom, Variables, PostgresHook и батч-оптимизация трансфера (execute_values).
* **Базы данных:** 
  * **PostgreSQL (OLTP):** Источник сырых транзакционных данных.
  * **Greenplum (DWH):** Колоночное MPP-хранилище.
* **ELT / Инженерия:** Python (`requests`, `psycopg2`, `pandas`, `faker`), SQL.
* **Аналитика:** Metabase (BI), оконные функции (Window Functions), распределенные JOIN'ы.
* **Data Quality:** Поиск аномалий на стороне Greenplum перед сборкой витрин и ветвление через XCom.
* **UI Инструменты:** pgAdmin (для Postgres) и CloudBeaver (для Greenplum).

## 📁 Как всё устроено (Архитектура)

* `/analytics` — Библиотека SQL-запросов (Топ-10 отправителей, "спящие" клиенты, трекинг онбординга).
* `/dags` — Настройки оркестратора:
  * `bank_pipeline_dag.py` — Главный ELT конвейер. Ждет файл -> Генерирует сырые данные -> Качает курсы -> Быстро переносит данные в Greenplum (`pg_to_gp_transfer.py`) -> Собирает витрины внутри GP -> Проводит DQ проверки.
  * `clean_xcom_dag.py` — Служебный DAG для ежедневной очистки кэша Airflow.
* `/etl` — Python-модули:
  * `data_generator.py` — Имитация истории банка (клиенты, счета, транзакции).
  * `fetch_rates.py` — Интеграция с REST API для курсов валют.
  * `etl_pipeline.py` — Трансформация сырых данных в аналитическую витрину `dm_transactions_rub`.
  * `pg_to_gp_transfer.py` — Мощный скрипт батч-трансфера данных из Postgres в Greenplum.
  * `dq_checks.py` — Data Quality тесты.
  * `etl_pyspark_colab_example.py` — Полигон для PySpark.
* `/migrations` — Скрипты инициализации (`init_greenplum.sql`, триггеры).
* `start.sh` — Умный скрипт для запуска Docker, снятия DAG с паузы и развертывания инфраструктуры.
* `docker-compose.yml` и `.json` конфиги — Поднимают всю инфраструктуру и автоматически прокидывают доступы (IaC).

## 🚀 Как запустить проект (Боевая среда)

**1. Клонируйте репозиторий:**
```bash
git clone [https://github.com/fiesttta/e_bank_dwh.git](https://github.com/fiesttta/e_bank_dwh.git)
cd e_bank_dwh
```

**2. Разверните инфраструктуру (Docker):**
Скрипт сам создаст нужные папки, выдаст права и поднимет все контейнеры.

```bash
chmod +x start.sh
./start.sh
```

**3. Конвейер запустится сам (Airflow):**
В скрипте предусмотрено автоматическое создание триггер файла и снятие с паузы DAGа. Airflow увидит файл и запустит весь процесс ELT!

🎉 **Готово! Данные перенесены в Greenplum и готовы к анализу.**

## 🌐 Доступы к интерфейсам (Где смотреть результат)

### ⚙️ 1. Оркестратор (Apache Airflow)

* **URL:** [http://localhost:8080](http://localhost:8080)
* **Логин / Пароль:** `fiestta` / `fiestta`

### 📊 2. BI-система (Metabase)

* **URL:** [http://localhost:3000](http://localhost:3000)
* **Как подключить базы (PostgreSQL / Greenplum):**
  * Как к вам обращаться: **Пишем что угодно**
  * Для чего вы будете использовать Metabase?: **Тоже что угодно**
  * Добавьте свои данные:
    * Выберите тип: **PostgreSQL**
    * Connection string для PostgreSQL: `postgresql://fiestta:fiestta@db:5432/e_bank`
    * Connection string для Greenplum: `postgresql://gpadmin:gpadmin@greenplum:5432/e_bank_dwh`

### 🐘 3. Управление Greenplum (CloudBeaver)

* **URL:** [http://localhost:8090](http://localhost:8090)
* В поле Administrator Credentials создайте пароль, после этого нажмите Next и Finish.
* Подключение к `e_bank_dwh` уже преднастроено через конфиг `cloudbeaver-data-sources.json`.

### 🛠 4. Управление сырым PostgreSQL (pgAdmin 4)

* **URL:** [http://localhost:5050](http://localhost:5050)
* **Логин:** `admin@admin.com` / **Пароль:** `admin`
* Серверы подтянутся автоматически из `pgadmin-servers.json` (потребуется только ввести пароль БД для подключения).