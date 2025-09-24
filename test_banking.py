import csv
import pytest
from banking import BankSystem

@pytest.fixture
def bank_env(tmp_path):
    bank_csv = tmp_path / "bank.csv"
    with open(bank_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id","first_name","last_name","password",
            "checking_balance","checking_active","checking_overdrafts",
            "savings_balance","savings_active","savings_overdrafts"
        ])
        writer.writeheader()
        writer.writerow({
            "id": 10001, "first_name": "Alice", "last_name": "A", "password": "pass1",
            "checking_balance": "100.00", "checking_active": "True", "checking_overdrafts": "0",
            "savings_balance": "50.00", "savings_active": "True", "savings_overdrafts": "0",
        })
    bs = BankSystem(str(bank_csv))
    bs.load_from_csv()
    return bs

def test_login(bank_env):
    user = bank_env.login(10001, "pass1")
    assert user.first_name == "Alice"

def test_deposit(bank_env):
    bank_env.login(10001, "pass1")
    msg = bank_env.deposit("checking", 50)
    assert "Deposit successful" in msg or "Account reactivated" in msg

def test_withdraw_limit(bank_env):
    bank_env.login(10001, "pass1")
    msg = bank_env.withdraw("checking", 200)
    assert "Cannot withdraw more than $100" in msg

def test_internal_transfer(bank_env):
    bank_env.login(10001, "pass1")
    msg = bank_env.transfer("checking", "savings", 20)
    assert "Transfer successful" in msg

def test_overdraft_fee_and_deactivate(bank_env):
    bank_env.login(10001, "pass1")
    bank_env.withdraw("checking", 95)
    msg2 = bank_env.withdraw("checking", 95)
    assert "Account deactivated" in msg2