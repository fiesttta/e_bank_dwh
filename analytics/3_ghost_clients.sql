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
