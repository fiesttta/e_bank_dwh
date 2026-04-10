-- Вывод топ-10 самых активных отправителей денег (включая банкоматы)
SELECT COALESCE(c.full_name, 'Внесение через банкомат') AS sender_name,
-- Вывод общей суммы
SUM(t.amount) AS total_sent
FROM transactions AS t
LEFT JOIN accounts a
	ON t.from_account_id = a.account_id
LEFT JOIN clients c
	ON a.client_id = c.client_id
-- Группировка по 1 столбцу и сортировка по сумме
GROUP BY 1
ORDER BY total_sent DESC
LIMIT 10;