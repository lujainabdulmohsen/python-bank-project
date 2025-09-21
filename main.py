from banking import BankSystem

def pause():
    input("Press Enter to continue...")

def prompt_float(msg, default=0.0):
    s = input(msg).strip()
    return float(s) if s else float(default)

def show_accounts(user):
    print("\n--- Accounts ---")
    if user.checking is None and user.savings is None:
        print("No accounts yet.")
    else:
        chk = user.checking.balance if user.checking else None
        sav = user.savings.balance if user.savings else None
        print(f"Checking: {chk if chk is not None else 'N/A'}")
        print(f"Savings:  {sav if sav is not None else 'N/A'}")
    pause()

def login_menu(bs: BankSystem):
    while True:
        print("\n--- Logged In ---")
        print("1. View my accounts")
        print("2. Create missing account")
        print("3. Logout")
        print("4. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            show_accounts(bs.current)

        elif choice == "2":
            if bs.current is None:
                print("Login first.")
                pause()
                continue

            missing = []
            if bs.current.checking is None:
                missing.append("checking")
            if bs.current.savings is None:
                missing.append("savings")

            if not missing:
                print("You already have both accounts.")
                pause()
                continue

            print("You can create:", ", ".join(missing))
            for acc_type in missing:
                confirm = input(f"Do you want to create {acc_type}? (y/n): ").strip().lower()
                if confirm == "y":
                    amt = prompt_float(f"Initial deposit for {acc_type} (default 0): ", 0.0)
                    try:
                        user_id = bs.current.id
                        user_pwd = bs.current.password
                        bs.create_account(acc_type, amt)
                        print(f"{acc_type} created and saved to CSV.")
                        bs.load_from_csv()
                        bs.login(user_id, user_pwd)
                    except Exception as e:
                        print("Error:", e)
                    pause()
                else:
                    print(f"{acc_type} not created.")
                    pause()

        elif choice == "3":
            bs.logout()
            print("Logged out.")
            pause()
            return

        elif choice == "4":
            print("Goodbye!")
            raise SystemExit

        else:
            print("Invalid option.")
            pause()

def main():
    bs = BankSystem("bank.csv")
    bs.load_from_csv()

    while True:
        print("\n--- Blue Sky Bank ---")
        print("1. Login")
        print("2. Create new customer")
        print("3. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            cid = input("ID: ").strip()
            if not cid.isdigit():
                print("ID must be numbers only.")
                pause()
                continue
            pwd = input("Password: ").strip()
            try:
                user = bs.login(cid, pwd)
                print(f"Welcome, {user.first_name} {user.last_name}!")
                login_menu(bs)
            except Exception as e:
                print("Login failed:", e)
                pause()

        elif choice == "2":
            first = input("First name: ").strip()
            last = input("Last name: ").strip()
            pwd = input("Password: ").strip()
            open_checking = input("Open checking? (y/n): ").strip().lower() == "y"
            open_savings = input("Open savings? (y/n): ").strip().lower() == "y"
            checking_balance = prompt_float("Initial checking (default 0): ", 0.0) if open_checking else 0.0
            savings_balance = prompt_float("Initial savings (default 0): ", 0.0) if open_savings else 0.0
            try:
                customer = bs.add_customer(
                    first_name=first,
                    last_name=last,
                    password=pwd,
                    open_checking=open_checking,
                    open_savings=open_savings,
                    checking_balance=checking_balance,
                    savings_balance=savings_balance
                )
                print(f"Customer created. Your ID is {customer.id}")
                pause()
            except Exception as e:
                print("Error:", e)
                pause()

        elif choice == "3":
            print("Goodbye!")
            break

        else:
            print("Invalid option.")
            pause()

if __name__ == "__main__":
    main()