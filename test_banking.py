import unittest
from banking import BankSystem

class TestBankSystem(unittest.TestCase):
    def setUp(self):
        self.bs = BankSystem("test_bank.csv", log_path="test_transactions.csv")
        self.bs.customers = []
        self.bs.save_all_to_csv()

    def test_add_customer(self):
        c = self.bs.add_customer("Lujain", "Alsultan", "1234", open_checking=True)
        self.assertEqual(c.first_name, "Lujain")
        self.assertIsNotNone(c.checking)

    def test_deposit_and_withdraw(self):
        c = self.bs.add_customer("Test", "User", "1111", open_checking=True)
        self.bs.login(c.id, "1111")
        msg1 = self.bs.deposit("checking", 200)
        self.assertIn("Deposit successful", msg1)
        msg2 = self.bs.withdraw("checking", 50)
        self.assertIn("Withdraw successful", msg2)

    def test_transfer_between_accounts(self):
        c = self.bs.add_customer("Ali", "User", "2222", open_checking=True, open_savings=True)
        self.bs.login(c.id, "2222")
        self.bs.deposit("checking", 100)
        msg = self.bs.transfer("checking", "savings", 50)
        self.assertIn("Transfer successful", msg)

if __name__ == "__main__":
    unittest.main()