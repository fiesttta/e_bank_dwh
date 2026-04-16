-- Создание триггера для автоматичсеского обновления баланса
-- Создание функции
CREATE OR REPLACE FUNCTION fn_update_balance()
RETURNS TRIGGER AS $$
BEGIN
	-- Пополнение или перевод к нам
	IF NEW.tx_type IN ('cash_deposit', 'transfer') THEN
		UPDATE accounts
		SET balance = balance + NEW.amount
		WHERE account_id = NEW.to_account_id;
	END IF;

	-- Снятие или перевод от нас
	IF NEW.tx_type IN ('cash_withdrawal', 'transfer', 'payment') THEN
		UPDATE accounts
		SET balance = balance - NEW.amount
		WHERE account_id = NEW.from_account_id;
	END IF;

	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Вешанье триггера на таблицу транзакций
CREATE TRIGGER trg_after_insert_transaction
AFTER INSERT ON transactions
FOR EACH ROW
EXECUTE FUNCTION fn_update_balance();