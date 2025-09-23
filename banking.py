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
        self.balance = float(balance)
        self.active = bool(active)
        self.overdraft_count = int(overdraft_count)

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
                    chk_bal = row.get("checking_balance") or ""
                    chk_act = row.get("checking_active") or ""
                    chk_odc = row.get("checking_overdrafts") or ""
                    sav_bal = row.get("savings_balance") or ""
                    sav_act = row.get("savings_active") or ""
                    sav_odc = row.get("savings_overdrafts") or ""
                    checking = None
                    savings = None
                    if chk_bal != "":
                        checking = Account("checking", float(chk_bal), (chk_act == "True"), int(chk_odc or 0))
                    if sav_bal != "":
                        savings = Account("savings", float(sav_bal), (sav_act == "True"), int(sav_odc or 0))
                    c = Customer(int(row["id"]), row["first_name"], row["last_name"], row["password"], checking, savings)
                    self.customers.append(c)
        except FileNotFoundError:
            self.customers = []

    def save_all_to_csv(self):
        fieldnames = [
            "id","first_name","last_name","password",
            "checking_balance","checking_active","checking_overdrafts",
            "savings_balance","savings_active","savings_overdrafts"
        ]
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for c in self.customers:
                chk_bal = f"{c.checking.balance:.2f}" if c.checking else ""
                chk_act = str(c.checking.active) if c.checking else ""
                chk_odc = str(c.checking.overdraft_count) if c.checking else ""
                sav_bal = f"{c.savings.balance:.2f}" if c.savings else ""
                sav_act = str(c.savings.active) if c.savings else ""
                sav_odc = str(c.savings.overdraft_count) if c.savings else ""
                writer.writerow({
                    "id": c.id,
                    "first_name": c.first_name,
                    "last_name": c.last_name,
                    "password": c.password,
                    "checking_balance": chk_bal,
                    "checking_active": chk_act,
                    "checking_overdrafts": chk_odc,
                    "savings_balance": sav_bal,
                    "savings_active": sav_act,
                    "savings_overdrafts": sav_odc
                })

    def add_customer(self, first_name, last_name, password, open_checking=False, open_savings=False):
        if self.customers:
            new_id = max(c.id for c in self.customers) + 1
        else:
            new_id = 10001
        checking = Account("checking", 0.0) if open_checking else None
        savings  = Account("savings", 0.0) if open_savings else None
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

    def create_account(self, account_type):
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
            c.checking = Account("checking", 0.0)
            acc = c.checking
        else:
            if c.savings:
                raise ValueError("Savings account already exists.")
            c.savings = Account("savings", 0.0)
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

    def deposit(self, account_type, amount):
        if amount <= 0:
            return "Amount must be positive."
        try:
            acc = self._get_account(account_type)
        except Exception as e:
            return f"Error: {e}"
        was_inactive = not acc.active
        acc.balance += amount
        if acc.balance >= 0 and was_inactive:
            acc.active = True
            msg = f"Account reactivated. Deposit successful. New balance: {acc.balance:.2f}"
        else:
            msg = f"Deposit successful. New balance: {acc.balance:.2f}"
        self.save_all_to_csv()
        return msg

    def withdraw(self, account_type, amount):
        if amount <= 0:
            return "Amount must be positive."
        try:
            acc = self._get_account(account_type)
        except Exception as e:
            return f"Error: {e}"
        if not acc.active:
            return "Account is deactivated. Current balance: {:.2f}".format(acc.balance)
        if amount > 100:
            return "Cannot withdraw more than $100 in one transaction. Current balance: {:.2f}".format(acc.balance)
        acc.balance -= amount
        if acc.balance < 0:
            acc.balance -= 35
            acc.overdraft_count += 1
            if acc.overdraft_count > 2:
                acc.active = False
                msg = "Overdraft fee $35.00 applied. Account deactivated."
            else:
                msg = "Overdraft fee $35.00 applied."
        else:
            if not acc.active:
                acc.active = True
            msg = "Withdraw successful."
        self.save_all_to_csv()
        return "{} Current balance: {:.2f}".format(msg, acc.balance)

class TransactionLog:
    pass
