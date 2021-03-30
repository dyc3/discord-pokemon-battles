import unittest
from pkmntypes import *


class TestTransactions(unittest.TestCase):

	def test_transaction_parse(self):
		transaction = Transaction(type=0, name="DamageTransaction", args={})
		self.assertEqual(transaction.type, 0)
		self.assertEqual(transaction.name, "DamageTransaction")


if __name__ == "__main__":
	unittest.main()
