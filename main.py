from banking import BankSystem

def pause():
    input("Press Enter to continue...")

def prompt_float(msg, default=0.0):
    s = input(msg).strip()
    return float(s) if s else float(default)

def info(msg):
    print(msg)
    pause()

def choose_account():
    print("\nChoose account:")
    print("1. Checking")
    print("2. Savings")
    ch = input("Enter choice: ").strip()
    if ch == "1":
        return "checking"
    if ch == "2":
        return "savings"
    return None

def show_accounts(bs: BankSystem):
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

def withdraw_menu(bs: BankSystem):
    if bs.current is None:
        info("Login first.")
        return
    acc_type = choose_account()
    if not acc_type:
        info("Invalid account choice.")
        return
    amt = prompt_float("Amount: ", 0.0)
    msg = bs.withdraw(acc_type, amt)
    info(msg)

def deposit_menu(bs: BankSystem):
    if bs.current is None:
        info("Login first.")
        return
    acc_type = choose_account()
    if not acc_type:
        info("Invalid account choice.")
        return
    amt = prompt_float("Amount: ", 0.0)
    msg = bs.deposit(acc_type, amt)
    info(msg)

def create_missing(bs: BankSystem):
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

def login_menu(bs: BankSystem):
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
        print("5. Logout")
        print("6. Exit")
        choice = input("Choose: ").strip()
        actions = {
            "1": lambda: show_accounts(bs),
            "2": lambda: withdraw_menu(bs),
            "3": lambda: deposit_menu(bs),
            "4": lambda: create_missing(bs),
            "5": do_logout,
            "6": lambda: (print("Goodbye!"), exit()),
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
