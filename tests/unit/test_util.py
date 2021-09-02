import unittest
from turns import *
from pkmntypes import *
from typing import Union
import util
from parameterized import parameterized, parameterized_class
from hypothesis import given, reproduce_failure, strategies as st


class TestHumanReadables(unittest.TestCase):

	@parameterized.expand(
		[
			({"a"}, "[a]"),
			(["a", "b", "c"], "[a][b][c]"), # using a list to guarentee iteration order
		]
	)
	def test_taggify(self, tags: set[str], pretty: str):
		self.assertEqual(util.taggify(tags), pretty)

	@parameterized.expand([
		(1 << 2 | 1 << 5, {"Flying", "Rock"}),
	])
	def test_types_to_string(self, mask: int, tags: set[str]):
		self.assertEqual(util.type_to_string(mask), tags)

	@parameterized.expand([
		(3, {"Paralyze"}),
		(4 | 1 << 8, {"Poison", "Flinch"}),
	])
	def test_status_to_string(self, status: int, tags: set[str]):
		self.assertEqual(util.status_to_string(status), tags)


class TestTeamBuilders(unittest.TestCase):

	@given(
		st.lists(
			st.one_of(
				st.lists(st.builds(Pokemon), min_size=1, max_size=6), st.builds(Party)
			),
			min_size=2,
			max_size=2,
		)
	)
	def test_build_teams_single(self, args: list[Union[Party, list[Pokemon]]]):
		teams = util.build_teams_single(*args)
		self.assertEqual(len(teams), 2, "should create 2 teams")
		for team in teams:
			self.assertIsInstance(team, Team)
			self.assertEqual(len(team.parties), 1, "each team should have 1 party")
			for party in team.parties:
				self.assertIsInstance(party, Party)
				for pokemon in party.pokemon:
					self.assertIsInstance(pokemon, Pokemon)


if __name__ == "__main__":
	unittest.main()
