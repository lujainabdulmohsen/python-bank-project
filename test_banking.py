import unittest
from banking import BankSystem

class TestBankSystem(unittest.TestCase):
    def setUp(self):
        self.bs = BankSystem("test_bank.csv", log_path="test_transactions.csv")
        self.bs.customers = []
        self.bs.save_all_to_csv()

    def test_add_customer(self):
        c = self.bs.add_customer("Test", "User", "1234", open_checking=True)
        self.assertEqual(c.first_name, "Test")
        self.assertIsNotNone(c.checking)

    def test_deposit(self):
        c = self.bs.add_customer("Test", "User", "1234", open_checking=True)
        self.bs.login(c.id, "1234")
        result = self.bs.deposit("checking", 100)
        self.assertIn("Deposit successful", result)

    def test_withdraw_limit(self):
        c = self.bs.add_customer("Test", "User", "1234", open_checking=True)
        self.bs.login(c.id, "1234")
        result = self.bs.withdraw("checking", 200)  
        self.assertIn("Cannot withdraw more than $100", result)

if __name__ == "__main__":
    unittest.main()