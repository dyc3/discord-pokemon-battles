import functools
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


if __name__ == "__main__":
	unittest.main()
