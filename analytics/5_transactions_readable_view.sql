/*
Создание "Вьюхи" для удобного выведения данных 
без потери места на условном сервере
*/

CREATE OR REPLACE VIEW v_transactions_readable AS
SELECT
	t.tx_id,
	t.created_at,
	COALESCE(c.full_name, 'Банкомат') AS sender_name,
	t.amount,
	t.tx_type
FROM transactions t
LEFT JOIN accounts a ON t.from_account_id = a.account_id
LEFT JOIN clients c ON a.client_id = c.client_id;

/*
При следующем запросе:

SELECT * FROM v_transactions_readable
WHERE tx_type = 'cash_withdrawal'
LIMIT 5;

Примерный вывод:
"tx_id"	"created_at"			"sender_name"					"amount"	"tx_type"
8		"2025-11-09 20:32:10"	"Светлана Антоновна Аксенова"	39862.55	"cash_withdrawal"
27		"2025-09-05 00:04:36"	"Наина Львовна Щукина"			23783.93	"cash_withdrawal"
32		"2024-12-27 00:22:43"	"Олимпиада Руслановна Панова"	30187.34	"cash_withdrawal"
58		"2024-02-11 01:23:38"	"Савельева Ульяна Эдуардовна"	47418.66	"cash_withdrawal"
60		"2025-10-31 06:07:08"	"Шубина Полина Владиславовна"	12475.33	"cash_withdrawal"
*/