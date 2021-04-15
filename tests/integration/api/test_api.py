import functools
from turns import FightTurn
import unittest
from hypothesis import given, strategies as st
from pkmntypes import *
import util
import battleapi
import asyncio


class TestBattleApi(unittest.TestCase):

	def setUp(self):
		self.loop = asyncio.new_event_loop()
		asyncio.set_event_loop(self.loop)

	def tearDown(self):
		self.loop.close()

	@given(
		size_a=st.integers(min_value=1, max_value=6),
		size_b=st.integers(min_value=1, max_value=6),
	)
	def test_create_battle(self, size_a, size_b):

		async def go():
			party_a = [await battleapi.generate_pokemon() for _ in range(size_a)]
			party_b = [await battleapi.generate_pokemon() for _ in range(size_b)]
			teams = util.build_teams_single(party_a, party_b)
			result = await battleapi.create_battle(teams)
			self.assertIsInstance(result["bid"], int)
			self.assertGreaterEqual(result["bid"], 0)

		return self.loop.run_until_complete(go())

	def test_battle_results(self):

		async def go():
			party_a = Party(
				pokemon=[
					await battleapi.generate_pokemon(natdex=25, level=28, moves=[85])
				]
			)
			party_b = Party(
				pokemon=[
					await battleapi.generate_pokemon(natdex=396, level=9, moves=[17])
				]
			)
			teams = util.build_teams_single(party_a, party_b)
			result = await battleapi.create_battle(teams)
			bid = result["bid"]
			while True:
				await battleapi.submit_turn(bid, 0, FightTurn(move=0, party=1, slot=0))
				await battleapi.submit_turn(bid, 1, FightTurn(move=0, party=0, slot=0))
				round_result = await battleapi.simulate(bid)
				if round_result.ended:
					break
				for t in round_result.transactions:
					print(t.pretty())
			bresults = await battleapi.get_results(bid)
			self.assertEqual(bresults.parties[0].pokemon[0].NatDex, 25)
			self.assertEqual(bresults.parties[1].pokemon[0].NatDex, 396)
			self.assertEqual(bresults.parties[1].pokemon[0].CurrentHP, 0)
			self.assertEqual(bresults.winner, 0)

		return self.loop.run_until_complete(go())


if __name__ == "__main__":
	unittest.main()
