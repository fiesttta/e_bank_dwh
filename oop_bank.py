# Создаем чертеж (Класс) для Клиента
class BankClient:
    
    # 1. КОНСТРУКТОР (Свойства). Вызывается автоматически при создании клиента.
    # Слово self означает "я сам" (обращение объекта к самому себе)
    def __init__(self, full_name, email):
        self.full_name = full_name
        self.email = email
        self.accounts = {}  # Словарь для хранения счетов {номер_счета: баланс}

    # 2. МЕТОДЫ (Действия)
    def open_account(self, account_number):
        self.accounts[account_number] = 0.0 # Открываем счет с нулевым балансом
        print(f"🏦 Успех: Клиент {self.full_name} открыл счет {account_number}\n")

    def deposit(self, account_number, amount):
        if account_number in self.accounts:
            self.accounts[account_number] += amount
            print(f"💵 Зачислено {amount} руб. на счет {account_number}. \n")
        else:
            print("❌ Ошибка: Такого счета нет! \n")

    def withdraw(self, account_number, amount):
        if account_number in self.accounts:
            if self.accounts[account_number] < amount:
                print("❌ Ошибка: Недостаточно средств!\n")
            else:
                self.accounts[account_number] -= amount
                print(f"💵 Снято {amount} руб. со счета {account_number}.\n")

    def show_info(self):
        print("-" * 30)
        print(f"👤 Клиент: {self.full_name} | Email: {self.email}")
        print(f"💼 Открытые счета: {self.accounts}")
        print("-" * 30)

# --- А ТЕПЕРЬ МАГИЯ ООП В ДЕЙСТВИИ ---

# Мы берем наш "чертеж" BankClient и создаем по нему два реальных Объекта:
client1 = BankClient("Иван Иванов", "ivan@mail.ru")
client2 = BankClient("Анна Смирнова", "anna@gmail.com")

# Дергаем методы (заставляем объекты работать):
client1.open_account("RU12345")
client1.deposit("RU12345", 50000)
client1.withdraw("RU12345", 23000)

client2.open_account("RU98765")
client2.deposit("RU98765", 15000)
client2.withdraw("RU98765", 15001)

# Смотрим результат:
client1.show_info()
client2.show_info()