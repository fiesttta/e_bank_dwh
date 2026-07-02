#!/bin/bash

echo "/// Запуск и настройка проекта e_bank ///"
mkdir -p dags logs plugins etl
echo -e "AIRFLOW_UID=$(id -u)" > .env
sudo chown -R $(id -u):0 dags logs plugins etl
sudo chmod -R 755 dags logs plugins etl

echo "/// Запуск докер контейнеров ///"
sudo docker compose up -d

echo "/// Ожидаем пока Airflow скачает библы и запустит бд... ///"
while ! curl -s http://localhost:8080 > /dev/null; do
    sleep 5
done

echo "/// Airflow готов. Создание пользователя для Airflow ///" 
sudo docker exec -t e_bank_airflow airflow users create \
    --username fiestta \
    --password fiestta \
    --firstname fiestta \
    --lastname fiestta \
    --role Admin \
    --email fiestta@ebank.com || true

echo "/// Готово ///"
echo "- Airflow: http://localhost:8080"
echo "- Metabase: http://localhost:3000"
echo "- pgAdmin 4: http://localhost:5050"
echo "- CloudBeaver: http://localhost:8088"