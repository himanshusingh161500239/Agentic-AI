import unittest
from accounts import Account, get_share_price

class TestAccounts(unittest.TestCase):

    def test_get_share_price(self):
        self.assertEqual(get_share_price('AAPL'), 170.00)
        self.assertEqual(get_share_price('TSLA'), 250.00)
        self.assertEqual(get_share_price('GOOGL'), 2700.00)
        self.assertEqual(get_share_price('XYZ'), 100.00)  # Test default price

    def test_account_creation(self):
        account = Account("test_account")
        self.assertEqual(account.account_id, "test_account")
        self.assertEqual(account.balance, 0.0)
        self.assertEqual(account.holdings, {})
        self.assertEqual(len(account.transactions), 0)

        account2 = Account("test_account_2", initial_deposit=1000.0)
        self.assertEqual(account2.balance, 1000.0)
        self.assertEqual(len(account2.transactions), 1)
        self.assertEqual(account2.transactions[0]['type'], 'deposit')
        self.assertEqual(account2.transactions[0]['amount'], 1000.0)

    def test_deposit(self):
        account = Account("test_account")
        account.deposit(100.0)
        self.assertEqual(account.balance, 100.0)
        self.assertEqual(len(account.transactions), 1)
        self.assertEqual(account.transactions[0]['type'], 'deposit')
        self.assertEqual(account.transactions[0]['amount'], 100.0)

        with self.assertRaises(ValueError):
            account.deposit(-50.0)
        with self.assertRaises(ValueError):
            account.deposit(0)

    def test_withdraw(self):
        account = Account("test_account", initial_deposit=200.0)
        account.withdraw(50.0)
        self.assertEqual(account.balance, 150.0)
        self.assertEqual(len(account.transactions), 2)
        self.assertEqual(account.transactions[1]['type'], 'withdrawal')
        self.assertEqual(account.transactions[1]['amount'], 50.0)

        with self.assertRaises(ValueError):
            account.withdraw(-20.0)
        with self.assertRaises(ValueError):
            account.withdraw(0)
        with self.assertRaises(ValueError):
            account.withdraw(300.0)  # Insufficient funds

    def test_buy_shares(self):
        account = Account("test_account", initial_deposit=1000.0)
        account.buy_shares("AAPL", 5)
        self.assertEqual(account.balance, 1000.0 - (170.00 * 5))
        self.assertEqual(account.holdings["AAPL"], 5)
        self.assertEqual(len(account.transactions), 2)
        self.assertEqual(account.transactions[1]['type'], 'buy')
        self.assertEqual(account.transactions[1]['symbol'], 'AAPL')
        self.assertEqual(account.transactions[1]['quantity'], 5)
        self.assertEqual(account.transactions[1]['price'], 170.00)

        with self.assertRaises(ValueError):
            account.buy_shares("TSLA", -2)
        with self.assertRaises(ValueError):
            account.buy_shares("GOOGL", 100)  # Insufficient funds

    def test_sell_shares(self):
        account = Account("test_account", initial_deposit=1000.0)
        account.buy_shares("AAPL", 5)
        account.sell_shares("AAPL", 3)
        self.assertEqual(account.balance, 1000.0 - (170.00 * 5) + (170.00 * 3))
        self.assertEqual(account.holdings["AAPL"], 2)
        self.assertEqual(len(account.transactions), 3)
        self.assertEqual(account.transactions[2]['type'], 'sell')
        self.assertEqual(account.transactions[2]['symbol'], 'AAPL')
        self.assertEqual(account.transactions[2]['quantity'], 3)
        self.assertEqual(account.transactions[2]['price'], 170.00)


        account.sell_shares("AAPL", 2)
        self.assertNotIn("AAPL", account.holdings)

        with self.assertRaises(ValueError):
            account.sell_shares("AAPL", 1)  # Insufficient shares (now 0)
        with self.assertRaises(ValueError):
            account.sell_shares("TSLA", 1) #symbol not present
        with self.assertRaises(ValueError):
            account.sell_shares("AAPL", -1)

    def test_get_portfolio_value(self):
        account = Account("test_account", initial_deposit=1000.0)
        account.buy_shares("AAPL", 5)
        account.buy_shares("TSLA", 2)
        expected_value = account.balance + (5 * 170.00) + (2 * 250.00)
        self.assertEqual(account.get_portfolio_value(), expected_value)

    def test_get_profit_loss(self):
        account = Account("test_account", initial_deposit=1000.0)
        account.buy_shares("AAPL", 5)
        profit_loss = account.get_profit_loss()
        self.assertEqual(profit_loss, account.get_portfolio_value() - 1000.0)

        account2 = Account("test_account_2")
        self.assertEqual(account2.get_profit_loss(), account2.get_portfolio_value())


    def test_get_holdings(self):
       account = Account("test_account", initial_deposit=1000.0)
       account.buy_shares("AAPL", 5)
       holdings = account.get_holdings()
       self.assertEqual(holdings["AAPL"], 5)

       #test immutability
       holdings["TSLA"] = 10
       self.assertNotIn("TSLA", account.holdings)


    def test_get_transactions(self):
        account = Account("test_account", initial_deposit=100.0)
        account.deposit(50.0)
        transactions = account.get_transactions()
        self.assertEqual(len(transactions), 2)

        #test immutability
        transactions.append({"type": "test"})
        self.assertEqual(len(account.transactions), 2)


if __name__ == '__main__':
    unittest.main()
