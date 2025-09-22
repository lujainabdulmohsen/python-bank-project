import csv

class Customer:
    def __init__(self, id, first_name, last_name, password, checking=None, savings=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.checking = checking
        self.savings = savings

class Account:
    def __init__(self, type, balance, active=True, overdraft_count=0):
        self.type = type
        self.balance = balance
        self.active = active
        self.overdraft_count = overdraft_count

class BankSystem:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.customers = []
        self.current = None

    def load_from_csv(self):
        self.customers = []
        try:
            with open(self.csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    chk_raw = (row.get("checking") or "").strip()
                    sav_raw = (row.get("savings") or "").strip()
                    checking = Account("checking", float(chk_raw)) if chk_raw != "" else None
                    savings = Account("savings", float(sav_raw)) if sav_raw != "" else None
                    c = Customer(
                        int(row["id"]),
                        row["first_name"],
                        row["last_name"],
                        row["password"],
                        checking,
                        savings
                    )
                    self.customers.append(c)
        except FileNotFoundError:
            self.customers = []

    def save_all_to_csv(self):
        fieldnames = ["id","first_name","last_name","password","checking","savings","active","overdraft_count"]
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for c in self.customers:
                chk = f"{c.checking.balance:.2f}" if c.checking else ""
                sav = f"{c.savings.balance:.2f}" if c.savings else ""
                writer.writerow({
                    "id": c.id,
                    "first_name": c.first_name,
                    "last_name": c.last_name,
                    "password": c.password,
                    "checking": chk,
                    "savings": sav,
                    "active": "True",
                    "overdraft_count": 0
                })

    def add_customer(self, first_name, last_name, password,
                     open_checking=False, open_savings=False,
                     checking_balance=0.0, savings_balance=0.0):
        if self.customers:
            new_id = max(c.id for c in self.customers) + 1
        else:
            new_id = 10001
        checking = Account("checking", float(checking_balance)) if open_checking else None
        savings  = Account("savings", float(savings_balance)) if open_savings else None
        customer = Customer(new_id, first_name, last_name, password, checking, savings)
        self.customers.append(customer)
        self.save_all_to_csv()
        return customer

    def login(self, customer_id, password):
        for c in self.customers:
            if c.id == int(customer_id) and c.password == password:
                self.current = c
                return c
        raise PermissionError("invalid credentials")

    def logout(self):
        self.current = None

    def create_account(self, account_type, initial_balance=0.0):
        if self.current is None:
            raise PermissionError("login required")
        if account_type not in ("checking", "savings"):
            raise ValueError("invalid account type")
        c = self.current
        if c.checking and c.savings:
            raise ValueError("You already have both accounts.")
        if account_type == "checking":
            if c.checking:
                raise ValueError("Checking account already exists.")
            c.checking = Account("checking", float(initial_balance))
            acc = c.checking
        else:
            if c.savings:
                raise ValueError("Savings account already exists.")
            c.savings = Account("savings", float(initial_balance))
            acc = c.savings
        self.save_all_to_csv()
        return acc

    def _get_account(self, account_type):
        if self.current is None:
            raise PermissionError("login required")
        if account_type == "checking":
            if not self.current.checking:
                raise ValueError("No checking account.")
            return self.current.checking
        elif account_type == "savings":
            if not self.current.savings:
                raise ValueError("No savings account.")
            return self.current.savings
        else:
            raise ValueError("invalid account type")

    def withdraw(self, account_type, amount):
        acc = self._get_account(account_type)
        if not acc.active:
            return "Account is deactivated."
        if amount > 100:
            return "Cannot withdraw more than $100 in one transaction."
        acc.balance -= amount
        if acc.balance < 0:
            acc.balance -= 35
            acc.overdraft_count += 1
            if acc.overdraft_count == 2:
                acc.active = False
                self.save_all_to_csv()
                return "Overdraft fee $35.00 applied. Account deactivated."
            else:
                self.save_all_to_csv()
                return "Overdraft fee $35.00 applied."
        if acc.balance >= 0:
            acc.active = True
        self.save_all_to_csv()
        return f"Withdraw successful. New balance: {acc.balance:.2f}"

class TransactionLog:
    pass