-- Вывод всех счетов с самыми первымси транзакциями

-- Создается временная таблица с оконной функцией
WITH RankedTransactions AS (
    SELECT 
        a.account_id,
        t.tx_id,
        t.amount,
        t.tx_type,
        t.created_at,
        ROW_NUMBER() OVER(
			-- Разбивается на окна по номеру счета
            PARTITION BY a.account_id
			-- Внутри окна сортировка по дате по возрастанию
            ORDER BY t.created_at ASC 
        ) as row_num
    FROM accounts a
    JOIN transactions t 
        ON a.account_id = t.from_account_id 
        OR a.account_id = t.to_account_id
)
-- Выборка из нашей временной таблицы
SELECT 
    account_id, 
    tx_id, 
    amount, 
    tx_type, 
    created_at
FROM RankedTransactions
-- Берем только самые первые транзакции!
WHERE row_num = 1; 

/* 
Примерный вывод:
"account_id" "tx_id"	"amount"	"tx_type"	"created_at"
1			  3302		 22007.98	"transfer"	"2023-12-01 19:06:56"
2			  3917		 18659.29	"transfer"	"2024-10-19 02:28:34"
3			  4804		 49516.33	"transfer"	"2026-04-07 01:22:17"
4			  786		 1490.47	"payment"	"2025-09-01 16:39:49"
5			  1164		 863.70		"transfer"	"2024-04-17 09:50:32"
6			  4331		 19190.33	"transfer"	"2026-02-14 21:54:17"
7			  4382		 20887.65	"payment"	"2024-06-08 19:23:55"
8			  4186		 18366.99	"transfer"	"2024-03-18 15:14:04"
9			  64		 33858.42	"payment"	"2023-10-19 22:09:52"
10			  846		 33280.52	"transfer"	"2023-05-27 22:56:23"
*/