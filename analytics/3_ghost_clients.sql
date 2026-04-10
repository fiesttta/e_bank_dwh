-- Поиск клиентов без открытых счетов
SELECT 
    full_name, 
    email, 
    registration_date
FROM clients
WHERE client_id NOT IN (
    -- Подзапрос для сбора ID
    SELECT client_id 
    FROM accounts 
    WHERE client_id IS NOT NULL
);

/* Так как при генерации данных мы установили то,
что для каждого клиента будет открыто от 1 до 4 счетов 
for _ in range(random.randint(1, 4)):
нету клиентов не открывших счет. Следовательно вывод = 0 строк */
