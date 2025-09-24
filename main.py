from banking import BankSystem

def pause():
    input("Press Enter to continue...")

def prompt_float(msg, default=0.0):
    s = input(msg).strip()
    try:
        return float(s) if s else float(default)
    except ValueError:
        print("Invalid amount. Using default:", default)
        return float(default)

def info(msg):
    print(msg)
    pause()

def choose_account():
    while True:
        print("\nChoose account:")
        print("1. Checking")
        print("2. Savings")
        ch = input("Enter choice: ").strip()
        if ch == "1":
            return "checking"
        if ch == "2":
            return "savings"
        print("Invalid choice. Please choose 1 or 2.")

def has_account(user, acc_type):
    if acc_type == "checking":
        return user.checking is not None
    if acc_type == "savings":
        return user.savings is not None
    return False

def show_accounts(bs):
    if bs.current is None:
        info("Login first.")
        return
    u = bs.current
    print("\n--- Accounts ---")
    if u.checking is None and u.savings is None:
        print("No accounts yet.")
    else:
        if u.checking:
            line = f"Checking: {u.checking.balance:.2f}"
            if not u.checking.active or u.checking.overdraft_count > 0:
                status = "inactive" if not u.checking.active else "active"
                line += f" | {status}, overdrafts={u.checking.overdraft_count}"
            print(line)
        else:
            print("Checking: N/A")
        if u.savings:
            line = f"Savings:  {u.savings.balance:.2f}"
            if not u.savings.active or u.savings.overdraft_count > 0:
                status = "inactive" if not u.savings.active else "active"
                line += f" | {status}, overdrafts={u.savings.overdraft_count}"
            print(line)
        else:
            print("Savings:  N/A")
    pause()

def withdraw_menu(bs):
    if bs.current is None:
        info("Login first.")
        return
    acc_type = choose_account()
    if not has_account(bs.current, acc_type):
        info(f"You don't have a {acc_type} account.")
        return
    amt = prompt_float("Amount: ", 0.0)
    msg = bs.withdraw(acc_type, amt)
    info(msg)

def deposit_menu(bs):
    if bs.current is None:
        info("Login first.")
        return
    acc_type = choose_account()
    if not has_account(bs.current, acc_type):
        info(f"You don't have a {acc_type} account.")
        return
    amt = prompt_float("Amount: ", 0.0)
    msg = bs.deposit(acc_type, amt)
    info(msg)

def transfer_menu(bs):
    if bs.current is None:
        info("Login first.")
        return
    print("\nTransfer Menu")
    print("1. Checking → Savings")
    print("2. Savings → Checking")
    print("3. To another customer")
    ch = input("Choose: ").strip()
    if ch == "1":
        from_type, to_type = "checking", "savings"
        if not has_account(bs.current, from_type):
            info("You don't have a checking account.")
            return
        if not has_account(bs.current, to_type):
            info("You don't have a savings account.")
            return
        amt = prompt_float("Amount: ", 0.0)
        msg = bs.transfer(from_type, to_type, amt)
        info(msg)
    elif ch == "2":
        from_type, to_type = "savings", "checking"
        if not has_account(bs.current, from_type):
            info("You don't have a savings account.")
            return
        if not has_account(bs.current, to_type):
            info("You don't have a checking account.")
            return
        amt = prompt_float("Amount: ", 0.0)
        msg = bs.transfer(from_type, to_type, amt)
        info(msg)
    elif ch == "3":
        from_type = choose_account()
        if not has_account(bs.current, from_type):
            info(f"You don't have a {from_type} account.")
            return
        target_id = input("Target customer ID: ").strip()
        if not target_id.isdigit():
            info("Target ID must be numbers only.")
            return
        if int(target_id) == bs.current.id:
            info("Cannot transfer to your own ID here. Use internal transfer.")
            return
        target = next((c for c in bs.customers if c.id == int(target_id)), None)
        if target is None:
            info("Target customer not found.")
            return
        target_acc = choose_account()
        if target_acc not in ("checking", "savings"):
            info("Invalid target account type.")
            return
        if not has_account(target, target_acc):
            info(f"Target does not have a {target_acc} account.")
            return
        amt = prompt_float("Amount: ", 0.0)
        msg = bs.transfer(from_type, None, amt, target_customer_id=int(target_id), target_account_type=target_acc)
        info(msg)
    else:
        info("Invalid choice.")

def fetch_all_user_tx(bs):
    return bs.recent_transactions(limit=0)

def print_tx_rows(rows):
    for r in rows:
        print((
            f"[{r['timestamp']}] {r['action'].upper()} {r['account_type'] or '-'} "
            f"amt={r['amount'] or '0.00'} fee={r['fee'] or '0.00'} "
            f"{r['prev_balance'] or '-'} -> {r['new_balance'] or '-'} "
            f"status={r['status']} msg={r['message']}"
        ))

def show_transactions_all(bs):
    if bs.current is None:
        info("Login first.")
        return
    rows = fetch_all_user_tx(bs)
    if not rows:
        info("No transactions yet.")
        return
    print("\n--- All Transactions ---")
    print_tx_rows(rows)
    pause()

def show_transactions_filtered(bs, filter_kind):
    if bs.current is None:
        info("Login first.")
        return
    rows = fetch_all_user_tx(bs)
    if filter_kind == "checking":
        rows = [r for r in rows if r["action"] in ("deposit", "withdraw") and r["account_type"] == "checking"]
        title = "Checking Deposits/Withdrawals"
    elif filter_kind == "savings":
        rows = [r for r in rows if r["action"] in ("deposit", "withdraw") and r["account_type"] == "savings"]
        title = "Savings Deposits/Withdrawals"
    elif filter_kind == "external":
        rows = [r for r in rows if r["action"] == "transfer" and ":" in (r["account_type"] or "")]
        title = "External Transfers"
    else:
        info("Invalid filter.")
        return
    if not rows:
        info("No transactions for this selection.")
        return
    print(f"\n--- {title} ---")
    print_tx_rows(rows)
    pause()

def transactions_menu(bs):
    while True:
        print("\n--- Transactions Menu ---")
        print("1. View all")
        print("2. Checking only")
        print("3. Savings only")
        print("4. External transfers only")
        print("5. Back")
        ch = input("Choose: ").strip()
        if ch == "1":
            show_transactions_all(bs)
        elif ch == "2":
            show_transactions_filtered(bs, "checking")
        elif ch == "3":
            show_transactions_filtered(bs, "savings")
        elif ch == "4":
            show_transactions_filtered(bs, "external")
        elif ch == "5":
            return
        else:
            info("Invalid choice.")

def create_missing(bs):
    if bs.current is None:
        info("Login first.")
        return
    missing = []
    if bs.current.checking is None:
        missing.append("checking")
    if bs.current.savings is None:
        missing.append("savings")
    if not missing:
        info("You already have both accounts.")
        return
    print("You can create:", ", ".join(missing))
    for acc_type in missing:
        confirm = input(f"Do you want to create {acc_type}? (y/n): ").strip().lower()
        if confirm == "y":
            try:
                uid, pwd = bs.current.id, bs.current.password
                bs.create_account(acc_type)
                print(f"{acc_type.capitalize()} account created.")
                bs.load_from_csv()
                bs.login(uid, pwd)
            except Exception as e:
                print(f"Error: {e}")
            pause()
        elif confirm == "n":
            info(f"{acc_type} not created.")
        else:
            info("Invalid choice. Please enter y or n.")

def login_menu(bs):
    def do_logout():
        bs.logout()
        info("Logged out.")
        return "back"
    while True:
        print("\n--- Logged In ---")
        print("1. View my accounts")
        print("2. Withdraw")
        print("3. Deposit")
        print("4. Create missing account")
        print("5. Transactions")
        print("6. Transfer")
        print("7. Logout")
        print("8. Exit")
        choice = input("Choose: ").strip()
        actions = {
            "1": lambda: show_accounts(bs),
            "2": lambda: withdraw_menu(bs),
            "3": lambda: deposit_menu(bs),
            "4": lambda: create_missing(bs),
            "5": lambda: transactions_menu(bs),
            "6": lambda: transfer_menu(bs),
            "7": do_logout,
            "8": lambda: (print("Goodbye!"), exit()),
        }
        act = actions.get(choice)
        if act:
            res = act()
            if res == "back":
                return
        else:
            info("Invalid option.")

def main():
    bs = BankSystem("bank.csv")
    bs.load_from_csv()
    while True:
        print("\n--- Blue Sky Bank ---")
        print("1. Login")
        print("2. Create account")
        print("3. Exit")
        choice = input("Choose: ").strip()
        if choice == "1":
            cid = input("ID: ").strip()
            if not cid.isdigit():
                info("ID must be numbers only.")
                continue
            pwd = input("Password: ").strip()
            try:
                u = bs.login(cid, pwd)
                print(f"Welcome, {u.first_name} {u.last_name}!")
                login_menu(bs)
            except Exception as e:
                info(f"Login failed: {e}")
        elif choice == "2":
            first = input("First name: ").strip()
            last = input("Last name: ").strip()
            pwd = input("Password: ").strip()
            open_checking = input("Create checking account? (y/n): ").strip().lower() == "y"
            open_savings  = input("Create savings account?  (y/n): ").strip().lower() == "y"
            try:
                c = bs.add_customer(
                    first_name=first,
                    last_name=last,
                    password=pwd,
                    open_checking=open_checking,
                    open_savings=open_savings
                )
                info(f"Customer created. Your ID is {c.id}")
            except Exception as e:
                info(f"Error: {e}")
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            info("Invalid option.")

if __name__ == "__main__":
    main()