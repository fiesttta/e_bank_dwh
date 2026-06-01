import requests
from datetime import datetime
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook

def fetch_and_save_rates():
    print("||| Загрузка реальных курсов валют... |||")

    # берем переменную из Airflow
    api_url = Variable.get("RATES_API_URL")

    # берем данные с инета
    response = requests.get(api_url)
    data = response.json()

    # usd как базовая валюта
    rates = data.get("rates", {})
    usd_to_rub = rates.get("RUB")
    usd_to_eur = rates.get("EUR")

    if not usd_to_rub or not usd_to_eur:
        raise ValueError("||| API не отдал валюты |||")
    
    # курс евро к рублю
    eur_to_rub = round(usd_to_rub / usd_to_eur, 4)
    usd_to_rub = round(usd_to_rub, 4)

    today = datetime.now().date()

    print(f"||| Актуальные курсы на {today}: USD = {usd_to_rub} руб, EUR = {eur_to_rub} руб. |||")

    hook = PostgresHook(postgres_conn_id="e_bank_conn")
    conn = hook.get_conn()
    cur = conn.cursor()

    insert_query = """
        INSERT INTO currency_rates (currency_code, rate_to_rub, effective_date)
        VALUES ('USD', %s, %s), ('EUR', %s, %s);
    """
    cur.execute(insert_query, (usd_to_rub, today, eur_to_rub, today))

    conn.commit()
    cur.close()
    conn.close()
    print("||| Актуальные курсы сохранены в Базу Данных. |||")
