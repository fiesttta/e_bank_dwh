#!/bin/bash

echo "запуск и настройка проекта e_bank"
mkdir -p dags logs plugins etl
echo -e "AIRFLOW_UID=$(id -u)" > .env
sudo chown -R $(id -u):0 dags logs plugins etl
sudo chmod -R 755 dags logs plugins etl

echo "запуск докер контейнеров"
sudo docker compose up -d

echo "готово. Airflow нужно пару минут на загрузку"