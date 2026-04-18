'''Так как PySpark ни в какую не хотел заводиться на Windows, 
скрипт был адаптирован для работы в Google Colab и Linux'''

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, coalesce, when, round as spark_round

print("Запуск кластера PySpark в Colab...")
# Создание точки входа
spark = SparkSession.builder.appName("Colab_ETL").master("local[*]").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

print("Загрузка сырых данных в память...")
# Транзакции
tx_data = [
    (1, 'transfer', 500.0, 101, 102),
    (2, 'cash_deposit', 1000.0, None, 103),
    (3, 'payment', 150.0, 101, 104)
]
df_tx = spark.createDataFrame(tx_data, ["tx_id", "tx_type", "amount", "from_account_id", "to_account_id"])

# Счета
acc_data = [(101, 'USD'), (102, 'RUB'), (103, 'EUR'), (104, 'RUB')]
df_acc = spark.createDataFrame(acc_data, ["account_id", "currency"])

# Курсы валют
rates_data = [('USD', 95.0), ('EUR', 105.0)]
df_rates = spark.createDataFrame(rates_data, ["currency_code", "rate_to_rub"])

print("Распределенные вычисления (Трансформация)...")
# Джоины отправителя и получателя
df_joined = df_tx.join(df_acc.alias("a_from"), col("from_account_id") == col("a_from.account_id"), "left") \
                 .join(df_acc.alias("a_to"), col("to_account_id") == col("a_to.account_id"), "left")

# Определение финальной валюты через Coalesce
df_with_currency = df_joined.withColumn("final_currency", coalesce(col("a_from.currency"), col("a_to.currency")))

# Подтягивание курсов
df_with_rates = df_with_currency.join(df_rates, col("final_currency") == col("currency_code"), "left")

# Конвертация валют в рубли
df_final = df_with_rates.withColumn(
    "amount_rub",
    when(col("final_currency") == 'RUB', col("amount"))
    .otherwise(spark_round(col("amount") * col("rate_to_rub"), 2))
)

# Нужные колонки для итоговой витрины
dm_transactions_rub = df_final.select("tx_id", "tx_type", "final_currency", "amount", "amount_rub")

print("Итоговая витрина данных:")
# Запуск всех вычислений
dm_transactions_rub.show()