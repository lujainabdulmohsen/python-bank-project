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
                    chk = float(chk_raw) if chk_raw not in ("", "") else 0.0
                    sav = float(sav_raw) if sav_raw not in ("", "") else 0.0
                    checking = Account("checking", chk) if chk != 0 else None
                    savings = Account("savings", sav) if sav != 0 else None
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

    def add_customer(self, first_name, last_name, password,
                     open_checking=False, open_savings=False,
                     checking_balance=0.0, savings_balance=0.0):

        if self.customers:
            new_id = max(c.id for c in self.customers) + 1
        else:
            new_id = 10001

        checking = Account("checking", float(checking_balance)) if open_checking else None
        savings = Account("savings", float(savings_balance)) if open_savings else None

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

    def save_all_to_csv(self):
        fieldnames = ["id","first_name","last_name","password","checking","savings","active","overdraft_count"]
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for c in self.customers:
                chk = f"{c.checking.balance:.2f}" if c.checking else "0"
                sav = f"{c.savings.balance:.2f}" if c.savings else "0"
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

class TransactionLog:
    pass