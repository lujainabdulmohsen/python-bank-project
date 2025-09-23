# python-bank-project


# Blue Sky Bank 



Blue Sky Bank is a simple command line banking application built with Python.
It lets customers create accounts, log in, and manage their money through a text-based menu. 

# Technical Requirements


Customers can register as new users and open checking or savings accounts—or both.
They log in with an ID and password, and once inside, they can only view their own accounts.
The withdrawal feature is fully implemented.
Customers may withdraw money from either account, but never more than $100 in a single transaction.
If a withdrawal causes the account to go negative, an overdraft fee of $35 is applied.
After more than two overdrafts, the account is deactivated.
The deposit feature is also implemented.
Deposits increase the account balance, and if the balance returns to zero or above, the account is reactivated automatically.
Account state (balance, active/inactive, overdrafts) is saved in bank.csv and persists between sessions.
When viewing accounts, only the balance is shown by default, while status and overdrafts appear only if relevant.


⸻

# Technologies Used
	•	Python 3
	•	CSV file storage
	•	Command Line Interface (CLI) menus