import unittest
from pkmntypes import *


class TestTransactions(unittest.TestCase):

	def test_transaction_parse(self):
		transaction = Transaction(type=0, name="DamageTransaction", args={})
		self.assertEqual(transaction.type, 0)
		self.assertEqual(transaction.name, "DamageTransaction")

	def test_transaction_pretty(self):
		transaction = Transaction(
			type=0,
			name="DamageTransaction",
			args={
				"Target": {
					"Pokemon": {
						"Name":
						"Altaria",
						"NatDex":
						334,
						"Level":
						53,
						"Ability":
						60,
						"TotalExperience":
						144410,
						"Gender":
						0,
						"IVs": [1, 5, 0, 3, 5, 2],
						"EVs": [0, 4, 41, 4, 10, 19],
						"Nature":
						8,
						"Stats": [143, 82, 105, 81, 120, 92],
						"StatModifiers": [0, 0, 0, 0, 0, 0, 0, 0, 0],
						"StatusEffects":
						0,
						"CurrentHP":
						143,
						"HeldItem": {
							"Id": 0,
							"Name": "",
							"Category": 0,
							"FlingPower": 0,
							"FlingEffect": 0,
							"Flags": 0
						},
						"Moves": [
							{
								"Id": 457,
								"CurrentPP": 5,
								"MaxPP": 5,
								"Name": "Head Smash",
								"Type": 32,
								"Category": 1,
								"Targets": 10,
								"Priority": 0,
								"Power": 150,
								"Accuracy": 80,
								"InitialMaxPP": 5,
								"MinHits": 0,
								"MaxHits": 0,
								"MinTurns": 0,
								"MaxTurns": 0,
								"Drain": -50,
								"Healing": 0,
								"CritRate": 0,
								"AilmentChance": 0,
								"FlinchChance": 0,
								"StatChance": 0,
								"Flags": 18448
							}, {
								"Id": 397,
								"CurrentPP": 20,
								"MaxPP": 20,
								"Name": "Rock Polish",
								"Type": 32,
								"Category": 0,
								"Targets": 7,
								"Priority": 0,
								"Power": 0,
								"Accuracy": 0,
								"InitialMaxPP": 20,
								"MinHits": 0,
								"MaxHits": 0,
								"MinTurns": 0,
								"MaxTurns": 0,
								"Drain": 0,
								"Healing": 0,
								"CritRate": 0,
								"AilmentChance": 0,
								"FlinchChance": 0,
								"StatChance": 0,
								"Flags": 524288
							}, {
								"Id": 466,
								"CurrentPP": 5,
								"MaxPP": 5,
								"Name": "Ominous Wind",
								"Type": 128,
								"Category": 2,
								"Targets": 10,
								"Priority": 0,
								"Power": 60,
								"Accuracy": 100,
								"InitialMaxPP": 5,
								"MinHits": 0,
								"MaxHits": 0,
								"MinTurns": 0,
								"MaxTurns": 0,
								"Drain": 0,
								"Healing": 0,
								"CritRate": 0,
								"AilmentChance": 10,
								"FlinchChance": 0,
								"StatChance": 10,
								"Flags": 18432
							}, {
								"Id": 172,
								"CurrentPP": 25,
								"MaxPP": 25,
								"Name": "Flame Wheel",
								"Type": 512,
								"Category": 1,
								"Targets": 10,
								"Priority": 0,
								"Power": 60,
								"Accuracy": 100,
								"InitialMaxPP": 25,
								"MinHits": 0,
								"MaxHits": 0,
								"MinTurns": 0,
								"MaxTurns": 0,
								"Drain": 0,
								"Healing": 0,
								"CritRate": 0,
								"AilmentChance": 10,
								"FlinchChance": 0,
								"StatChance": 0,
								"Flags": 18512
							}
						],
						"Friendship":
						0,
						"OriginalTrainerID":
						0,
						"Type":
						32772
					}
				},
				"Move": {
					"Name": "Tackle",
				},
				"Damage": 14,
				"StatusEffect": 0,
			}
		)
		self.assertEqual(
			transaction.pretty(), "Altaria [Dragon] [Flying] took 14 damage."
		)


if __name__ == "__main__":
	unittest.main()
