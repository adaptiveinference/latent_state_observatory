# CHECK_TOKEN: PYC052

class BankAccount:
    def __init__(self, balance=0):
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount
        else:
            raise ValueError("Insufficient balance")

    def get_balance(self):
        return self.balance

# Example usage:
account = BankAccount(100)
account.deposit(50)
account.withdraw(20)
print(account.get_balance())  # Output: 120

# Check if the balance is valid
if account.get_balance() < 0:
    raise ValueError("Invalid balance")

# Check if the withdrawal amount is less than or equal to the balance
if account.withdraw(100) > account.get_balance():
    raise ValueError("Insufficient balance for withdrawal")

# Check if the deposit amount is greater than the balance
if account.deposit(50) > account.get_balance():
    raise ValueError("Insufficient balance for deposit")