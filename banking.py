import csv
import os

class Customer:
    def __init__(self, id, first_name, last_name, password, checking=None, savings=None):
        self.id = int(id)
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

class TransactionLog:
    FIELDS = [
        "customer_id","action","account_type",
        "amount","fee","prev_balance","new_balance","status","message"
    ]
    def __init__(self, csv_path="transactions.csv"):
        self.csv_path = csv_path
        need_header = not os.path.exists(self.csv_path) or os.path.getsize(self.csv_path) == 0
        if need_header:
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=self.FIELDS).writeheader()
    def append(self, **kw):
        row = {k: "" for k in self.FIELDS}
        row.update(kw)
        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=self.FIELDS).writerow(row)
    def list_for(self, customer_id, limit=20):
        try:
            with open(self.csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = [r for r in reader if str(r.get("customer_id")) == str(customer_id)]
                return rows[-limit:] if limit else rows
        except FileNotFoundError:
            return []

class BankSystem:
    def __init__(self, csv_path, log_path="transactions.csv"):
        self.csv_path = csv_path
        self.customers = []
        self.current = None
        self.log = TransactionLog(log_path)

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
        new_id = (max((c.id for c in self.customers), default=10000) + 1)
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

    def _get_account(self, account_type, customer=None):
        customer = customer or self.current
        if customer is None:
            raise PermissionError("login required")
        if account_type == "checking":
            if not customer.checking:
                raise ValueError("No checking account.")
            return customer.checking
        if account_type == "savings":
            if not customer.savings:
                raise ValueError("No savings account.")
            return customer.savings
        raise ValueError("invalid account type")

    def _customer_overdraft_total(self, customer):
        total = 0
        if customer.checking:
            total += customer.checking.overdraft_count
        if customer.savings:
            total += customer.savings.overdraft_count
        return total

    def _deactivate_customer_accounts(self, customer):
        if customer.checking:
            customer.checking.active = False
        if customer.savings:
            customer.savings.active = False

    def deposit(self, account_type, amount):
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return "Amount must be a number."
        if amount <= 0:
            return "Amount must be positive."
        try:
            acc = self._get_account(account_type)
        except Exception as e:
            return f"Error: {e}"
        was_user_deactivated = (
            (self.current.checking and not self.current.checking.active) or
            (self.current.savings and not self.current.savings.active)
        )
        prev = acc.balance
        acc.balance += amount
        if was_user_deactivated:
            all_solvent = True
            if self.current.checking and self.current.checking.balance < 0:
                all_solvent = False
            if self.current.savings and self.current.savings.balance < 0:
                all_solvent = False
            if all_solvent:
                if self.current.checking:
                    self.current.checking.active = True
                    self.current.checking.overdraft_count = 0
                if self.current.savings:
                    self.current.savings.active = True
                    self.current.savings.overdraft_count = 0
                msg = "All accounts reactivated. Deposit successful."
            else:
                msg = "Deposit successful."
        else:
            msg = "Deposit successful."
        self.save_all_to_csv()
        self.log.append(customer_id=self.current.id, action="deposit", account_type=account_type,
                        amount=f"{amount:.2f}", fee="0.00",
                        prev_balance=f"{prev:.2f}", new_balance=f"{acc.balance:.2f}",
                        status="ok", message=msg)
        return f"{msg} New balance: {acc.balance:.2f}"

    def withdraw(self, account_type, amount):
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return "Amount must be a number."
        if amount <= 0:
            return "Amount must be positive."
        try:
            acc = self._get_account(account_type)
        except Exception as e:
            return f"Error: {e}"
        if not acc.active:
            msg = f"Account is deactivated. Current balance: {acc.balance:.2f}"
            self.log.append(customer_id=self.current.id, action="withdraw", account_type=account_type,
                            amount=f"{amount:.2f}", fee="0.00",
                            prev_balance=f"{acc.balance:.2f}", new_balance=f"{acc.balance:.2f}",
                            status="error", message="deactivated")
            return msg
        if amount > 100:
            msg = f"Cannot withdraw more than $100 in one transaction. Current balance: {acc.balance:.2f}"
            self.log.append(customer_id=self.current.id, action="withdraw", account_type=account_type,
                            amount=f"{amount:.2f}", fee="0.00",
                            prev_balance=f"{acc.balance:.2f}", new_balance=f"{acc.balance:.2f}",
                            status="error", message="over limit")
            return msg
        b = acc.balance
        if b < 0:
            max_allowed = max(0.0, min(100.0, b + 65.0))
            if amount > max_allowed:
                msg = f"Overdraft limit reached. Max you can withdraw is ${max_allowed:.2f}. Current balance: {b:.2f}"
                self.log.append(customer_id=self.current.id, action="withdraw", account_type=account_type,
                                amount=f"{amount:.2f}", fee="0.00",
                                prev_balance=f"{b:.2f}", new_balance=f"{b:.2f}",
                                status="error", message="overdraft cap")
                return msg
        else:
            if amount > b:
                max_allowed = max(0.0, min(100.0, b + 65.0))
                if amount > max_allowed:
                    msg = f"Overdraft limit reached. Max you can withdraw is ${max_allowed:.2f}. Current balance: {b:.2f}"
                    self.log.append(customer_id=self.current.id, action="withdraw", account_type=account_type,
                                    amount=f"{amount:.2f}", fee="0.00",
                                    prev_balance=f"{b:.2f}", new_balance=f"{b:.2f}",
                                    status="error", message="overdraft cap")
                    return msg
        prev = acc.balance
        acc.balance -= amount
        fee = 0.0
        overdrafted_now = prev < 0 or acc.balance < 0
        if overdrafted_now:
            fee = 35.0
            acc.balance -= fee
            acc.overdraft_count += 1
            total = self._customer_overdraft_total(self.current)
            if total >= 3:
                self._deactivate_customer_accounts(self.current)
                msg = "Overdraft fee $35.00 applied. Account deactivated."
            else:
                msg = "Overdraft fee $35.00 applied."
        else:
            if not acc.active:
                acc.active = True
            msg = "Withdraw successful."
        self.save_all_to_csv()
        self.log.append(customer_id=self.current.id, action="withdraw", account_type=account_type,
                        amount=f"{amount:.2f}", fee=f"{fee:.2f}",
                        prev_balance=f"{prev:.2f}", new_balance=f"{acc.balance:.2f}",
                        status="ok", message=msg)
        return f"{msg} Current balance: {acc.balance:.2f}"

    def transfer(self, from_type, to_type, amount, target_customer_id=None, target_account_type=None):
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return "Amount must be a number."
        if amount <= 0:
            return "Amount must be positive."
        try:
            src = self._get_account(from_type)
        except Exception as e:
            return f"Error: {e}"
        if not src.active:
            return f"Source account is deactivated. Current balance: {src.balance:.2f}"
        if amount > 100:
            return f"Cannot transfer more than $100 in one transaction. Current balance: {src.balance:.2f}"
        if src.balance - amount < 0:
            return f"Insufficient funds. Current balance: {src.balance:.2f}"
        prev_src = src.balance
        if target_customer_id is None:
            if from_type == to_type:
                return "Cannot transfer to the same account."
            try:
                dst = self._get_account(to_type)
            except Exception as e:
                return f"Error: {e}"
            src.balance -= amount
            dst.balance += amount
            self.save_all_to_csv()
            self.log.append(customer_id=self.current.id, action="transfer",
                            account_type=f"{from_type}->{to_type}", amount=f"{amount:.2f}", fee="0.00",
                            prev_balance=f"{prev_src:.2f}", new_balance=f"{src.balance:.2f}",
                            status="ok", message="Internal transfer")
            chk_bal = f"{self.current.checking.balance:.2f}" if self.current.checking else "N/A"
            sav_bal = f"{self.current.savings.balance:.2f}" if self.current.savings else "N/A"
            return f"Transfer successful. checking={chk_bal}, savings={sav_bal}"
        if int(target_customer_id) == self.current.id:
            return "Cannot transfer to your own accounts here. Use internal transfer."
        target = next((c for c in self.customers if c.id == int(target_customer_id)), None)
        if target is None:
            return "Target customer not found."
        if target_account_type not in ("checking", "savings"):
            return "Invalid target account type."
        try:
            dst = self._get_account(target_account_type, customer=target)
        except Exception as e:
            return f"Error: {e}"
        src.balance -= amount
        dst.balance += amount
        self.save_all_to_csv()
        self.log.append(customer_id=self.current.id, action="transfer",
                        account_type=f"{from_type}->{target.id}:{target_account_type}",
                        amount=f"{amount:.2f}", fee="0.00",
                        prev_balance=f"{prev_src:.2f}", new_balance=f"{src.balance:.2f}",
                        status="ok", message=f"External transfer to {target.id}")
        return f"Transfer successful. {from_type}={src.balance:.2f}"

    def recent_transactions(self, limit=20):
        if self.current is None:
            raise PermissionError("login required")
        return self.log.list_for(self.current.id, limit=limit)