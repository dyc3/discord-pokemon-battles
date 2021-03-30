import unittest
from turns import *
import json


class TestTurns(unittest.TestCase):

	def test_turns_to_json(self):
		turn = FightTurn(party=0, slot=0, move=0)
		self.assertEqual(json.loads(turn.toJSON())["type"], 0)
		self.assertEqual(json.loads(turn.toJSON())["args"], turn.__dict__)

		turn = ItemTurn()
		self.assertEqual(json.loads(turn.toJSON())["type"], 1)
		self.assertEqual(json.loads(turn.toJSON())["args"], turn.__dict__)


if __name__ == "__main__":
	unittest.main()
