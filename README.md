# 🏦 E-Bank DWH & ETL Pipeline (Dockerized)

Это мой проект, в котором я с нуля спроектировал и построил аналитическое хранилище данных (DWH) для небольшого цифрового банка. 

Проект прошел путь от простых SQL-скриптов до **полностью докеризированной инфраструктуры**, которая разворачивается одной командой и управляется современным оркестратором.

## 📊 Результат работы (BI Dashboard в Metabase)
![E-Bank Dashboard](dashboard.png)

## 🛠 Что внутри? (Стек)
* **Инфраструктура:** Docker, Docker Compose
* **Оркестрация (Пайплайны):** Apache Airflow
* **Базы данных:** PostgreSQL (OLTP & OLAP слои)
* **ETL / Инженерия:** Python (psycopg2, pandas, faker), SQL
* **Data Quality:** Проверка данных и остановка при аномалиях
* **BI / Аналитика:** Metabase
* **Big Data:** PySpark (Google Colab)

## 📁 Как всё устроено (Архитектура)

* `/analytics` - Библиотека сложных SQL-запросов (CTE, Window Functions, Views) для поиска аномалий и топов.
* `/dags` - (DAGs) для Airflow.
  * `bank_pipeline_dag.py` - Генерация данных -> трансформация -> проверка качества.
* `/etl` — Сервис загрузки и трансформации данных.
  * `data_generator.py` - Инициализирует DDL-схемы и генерирует реалистичные данные (клиенты, счета, транзакции).
  * `dq_checks.py` - Скрипт проверок качества (Data Quality). Ищет дубликаты и клиентов-призраков.
  * `etl_pipeline.py` - Переносит данные из сырого слоя в аналитические витрины (конвертация валют, агрегации).
  * `etl_pyspark_colab_example` - Полигон для PySpark (пример обработки тех же данных в парадигме Big Data).
* `/migrations` - Скрипты уровня базы данных (например, умный триггер для авто-обновления баланса счетов).
* `.env` - Настройка UID для AIRFLOW (актуально для linux)
* `.gitignore` - То, что не должно попасть в гит 
* `dashboard.png` - Скрин для `README.md`
* `docker-compose.yml` - Поднимает БД, Airflow, Metabase и среду для скриптов.
* `oop_bank` - Простейшая ООП модель банка (класс BankClient с методами пополнения и снятия).

## 🚀 Как запустить у себя

**1. Клонируйте репозиторий:**
```bash
git clone https://github.com/fiesttta/e_bank_dwh
cd e_bank_dwh
```
**Настройте права для Airflow (Важно для Linux/macOS):**
```bash
echo -e "AIRFLOW_UID=$(id -u)" > .env
sudo chmod -R 755 dags logs plugins
```

**3. Поднимите инфраструктуру (БД и BI-систему):**
```bash
docker compose up -d
```

**4. Запустите автоматический конвейер (ETL):**
* Перейдите в интерфейс Airflow (ссылка ниже).
* Снимите DAG e_bank_daily_etl с паузы (синий переключатель слева).
* Нажмите кнопку **Play** (Trigger DAG.)
* Airflow сам сгенерирует данные, соберет витрины и проведет тестирование качества!

🎉 **Готово! Инфраструктура развернута и данные готовы к анализу**

## 🌐 Интерфейсы управления (Где смотреть результат)

### ⚙️ 1. Оркестратор (Apache Airflow)
* **URL:** [http://localhost:8080](http://localhost:8080)
* **Логин/Пароль: fiestta/fiestta**

### 📊 2. BI-система (Metabase)
* **URL:** [http://localhost:3000](http://localhost:3000)
* **Как подключить базу:**
  * Выберите тип: **PostgreSQL**
  * **Host:** `db` *(обращение идет по имени контейнера)*
  * **Database name:** `e_bank`
  * **Username:** `postgres`
  * **Password:** `fiestta`

### 🛠 3. Управление базой (pgAdmin 4)
* **URL:** [http://localhost:5050](http://localhost:5050)
* **Вход в интерфейс:** `admin@admin.com` / `admin`
* **Как подключить базу (Add New Server):**
  * Вкладка **General** -> Name: `E-Bank DB`
  * Вкладка **Connection**:
    * **Host name/address:** `db`
    * **Port:** `5432`
    * **Maintenance database:** `e_bank`
    * **Username:** `postgres`
    * **Password:** `fiestta`