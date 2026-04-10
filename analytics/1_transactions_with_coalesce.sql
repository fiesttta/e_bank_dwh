-- 1. Вывод всех транзакций с именами отправителей
SELECT t.tx_id,
-- Если имя отправителя будет NULL, оно будет заменено
COALESCE(c.full_name, 'Внесение через банкомат') AS sender_name,
t.amount,
t.tx_type 
FROM transactions AS t
LEFT JOIN accounts a
	ON t.from_account_id = a.account_id
LEFT JOIN clients c
	ON a.client_id = c.client_id;