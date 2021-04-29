import unittest
from turns import *
from pkmntypes import *
import util
from parameterized import parameterized, parameterized_class
from hypothesis import given, strategies as st


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


garbage_transactions = st.lists(
	st.builds(
		Transaction,
		type=st.integers(),
		name=st.text(min_size=1),
		args=st.dictionaries(
			st.text(),
			st.one_of(
				st.integers(), st.text(),
				st.dictionaries(
					st.text(),
					st.one_of(st.integers(), st.text()),
				)
			),
		)
	)
)
# yapf: disable
sampled_transactions = st.lists(
	st.sampled_from(
	[
	Transaction(type=0, name="UseMoveTransaction", args={'User': {'Party': 0, 'Slot': 0, 'Team': 0, 'Pokemon': {'Name': 'Pichu', 'NatDex': 172, 'Level': 30, 'Ability': 98, 'TotalExperience': 27000, 'Gender': 0, 'IVs': [0, 1, 2, 4, 0, 2], 'EVs': [13, 18, 17, 22, 32, 21], 'Nature': 8, 'Stats': [52, 30, 15, 28, 28, 43], 'StatModifiers': [0, 0, 0, 0, 0, 0, 0, 0, 0], 'StatusEffects': 0, 'CurrentHP': 52, 'HeldItem': {'Id': 0, 'Name': '', 'Category': 0, 'FlingPower': 0, 'FlingEffect': 0, 'Flags': 0}, 'Moves': [{'Id': 193, 'CurrentPP': 40, 'MaxPP': 40, 'Name': 'Foresight', 'Type': 1, 'Category': 0, 'Targets': 10, 'Priority': 0, 'Power': 0, 'Accuracy': 0, 'InitialMaxPP': 40, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 0, 'Flags': 280577, 'AffectedStat': 0, 'StatStages': 0}, {'Id': 433, 'CurrentPP': 5, 'MaxPP': 5, 'Name': 'Trick Room', 'Type': 8192, 'Category': 0, 'Targets': 12, 'Priority': -7, 'Power': 0, 'Accuracy': 0, 'InitialMaxPP': 5, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 0, 'Flags': 2048, 'AffectedStat': 0, 'StatStages': 0}, {'Id': 225, 'CurrentPP': 19, 'MaxPP': 20, 'Name': 'Dragon Breath', 'Type': 32768, 'Category': 2, 'Targets': 10, 'Priority': 0, 'Power': 60, 'Accuracy': 100, 'InitialMaxPP': 20, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 30, 'FlinchChance': 0, 'StatChance': 0, 'Flags': 18432, 'AffectedStat': 0, 'StatStages': 0}, {'Id': 232, 'CurrentPP': 35, 'MaxPP': 35, 'Name': 'Metal Claw', 'Type': 256, 'Category': 1, 'Targets': 10, 'Priority': 0, 'Power': 50, 'Accuracy': 95, 'InitialMaxPP': 35, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 10, 'Flags': 18448, 'AffectedStat': 1, 'StatStages': 1}], 'Friendship': 0, 'OriginalTrainerID': 0, 'Type': 4096}}, 'Target': {'Party': 1, 'Slot': 0, 'Team': 0, 'Pokemon': {'Name': 'Marowak', 'NatDex': 105, 'Level': 30, 'Ability': 49, 'TotalExperience': 27000, 'Gender': 0, 'IVs': [2, 4, 3, 1, 1, 4], 'EVs': [18, 9, 7, 24, 41, 11], 'Nature': 8, 'Stats': [77, 54, 72, 37, 56, 33], 'StatModifiers': [0, 0, 0, 0, 0, 0, 0, 0, 0], 'StatusEffects': 0, 'CurrentHP': 67, 'HeldItem': {'Id': 0, 'Name': '', 'Category': 0, 'FlingPower': 0, 'FlingEffect': 0, 'Flags': 0}, 'Moves': [{'Id': 18, 'CurrentPP': 19, 'MaxPP': 20, 'Name': 'Whirlwind', 'Type': 1, 'Category': 0, 'Targets': 10, 'Priority': -6, 'Power': 0, 'Accuracy': 0, 'InitialMaxPP': 20, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 0, 'Flags': 264193, 'AffectedStat': 0, 'StatStages': 0}, {'Id': 242, 'CurrentPP': 15, 'MaxPP': 15, 'Name': 'Crunch', 'Type': 65536, 'Category': 1, 'Targets': 10, 'Priority': 0, 'Power': 80, 'Accuracy': 100, 'InitialMaxPP': 15, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 20, 'Flags': 18452, 'AffectedStat': 2, 'StatStages': -1}, {'Id': 61, 'CurrentPP': 20, 'MaxPP': 20, 'Name': 'Bubble Beam', 'Type': 1024, 'Category': 2, 'Targets': 10, 'Priority': 0, 'Power': 65, 'Accuracy': 100, 'InitialMaxPP': 20, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 10, 'Flags': 18432, 'AffectedStat': 5, 'StatStages': -1}, {'Id': 457, 'CurrentPP': 5, 'MaxPP': 5, 'Name': 'Head Smash', 'Type': 32, 'Category': 1, 'Targets': 10, 'Priority': 0, 'Power': 150, 'Accuracy': 80, 'InitialMaxPP': 5, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': -50, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 0, 'Flags': 18448, 'AffectedStat': 0, 'StatStages': 0}], 'Friendship': 0, 'OriginalTrainerID': 0, 'Type': 16}}, 'Move': {'Id': 225, 'CurrentPP': 19, 'MaxPP': 20, 'Name': 'Dragon Breath', 'Type': 32768, 'Category': 2, 'Targets': 10, 'Priority': 0, 'Power': 60, 'Accuracy': 100, 'InitialMaxPP': 20, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 30, 'FlinchChance': 0, 'StatChance': 0, 'Flags': 18432, 'AffectedStat': 0, 'StatStages': 0}}),
	Transaction( name="PPTransaction", args={ 'Move': {'Id': 225,'CurrentPP': 19,'MaxPP': 20,'Name': 'Dragon Breath','Type': 32768,'Category': 2,'Targets': 10,'Priority': 0,'Power': 60,'Accuracy': 100,'InitialMaxPP': 20,'MinHits': 0,'MaxHits': 0,'MinTurns': 0,'MaxTurns': 0,'Drain': 0,'Healing': 0,'CritRate': 0,'AilmentChance': 30,'FlinchChance': 0,'StatChance': 0,'Flags': 18432,'AffectedStat': 0,'StatStages': 0},'Amount': -1}),
	Transaction(type=1, name="DamageTransaction", args={'Target': {'Party': 1, 'Slot': 0, 'Team': 0, 'Pokemon': {'Name': 'Marowak', 'NatDex': 105, 'Level': 30, 'Ability': 49, 'TotalExperience': 27000, 'Gender': 0, 'IVs': [2, 4, 3, 1, 1, 4], 'EVs': [18, 9, 7, 24, 41, 11], 'Nature': 8, 'Stats': [77, 54, 72, 37, 56, 33], 'StatModifiers': [0, 0, 0, 0, 0, 0, 0, 0, 0], 'StatusEffects': 0, 'CurrentHP': 67, 'HeldItem': {'Id': 0, 'Name': '', 'Category': 0, 'FlingPower': 0, 'FlingEffect': 0, 'Flags': 0}, 'Moves': [{'Id': 18, 'CurrentPP': 19, 'MaxPP': 20, 'Name': 'Whirlwind', 'Type': 1, 'Category': 0, 'Targets': 10, 'Priority': -6, 'Power': 0, 'Accuracy': 0, 'InitialMaxPP': 20, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 0, 'Flags': 264193, 'AffectedStat': 0, 'StatStages': 0}, {'Id': 242, 'CurrentPP': 15, 'MaxPP': 15, 'Name': 'Crunch', 'Type': 65536, 'Category': 1, 'Targets': 10, 'Priority': 0, 'Power': 80, 'Accuracy': 100, 'InitialMaxPP': 15, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 20, 'Flags': 18452, 'AffectedStat': 2, 'StatStages': -1}, {'Id': 61, 'CurrentPP': 20, 'MaxPP': 20, 'Name': 'Bubble Beam', 'Type': 1024, 'Category': 2, 'Targets': 10, 'Priority': 0, 'Power': 65, 'Accuracy': 100, 'InitialMaxPP': 20, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 10, 'Flags': 18432, 'AffectedStat': 5, 'StatStages': -1}, {'Id': 457, 'CurrentPP': 5, 'MaxPP': 5, 'Name': 'Head Smash', 'Type': 32, 'Category': 1, 'Targets': 10, 'Priority': 0, 'Power': 150, 'Accuracy': 80, 'InitialMaxPP': 5, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': -50, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 0, 'Flags': 18448, 'AffectedStat': 0, 'StatStages': 0}], 'Friendship': 0, 'OriginalTrainerID': 0, 'Type': 16}}, 'Move': {'Id': 225, 'CurrentPP': 19, 'MaxPP': 20, 'Name': 'Dragon Breath', 'Type': 32768, 'Category': 2, 'Targets': 10, 'Priority': 0, 'Power': 60, 'Accuracy': 100, 'InitialMaxPP': 20, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 30, 'FlinchChance': 0, 'StatChance': 0, 'Flags': 18432, 'AffectedStat': 0, 'StatStages': 0}, 'Damage': 10, 'StatusEffect': 0}),
	Transaction(type=0, name="UseMoveTransaction", args={'User': {'Party': 1, 'Slot': 0, 'Team': 1, 'Pokemon': {'Name': 'Marowak', 'NatDex': 105, 'Level': 30, 'Ability': 49, 'TotalExperience': 27000, 'Gender': 0, 'IVs': [2, 4, 3, 1, 1, 4], 'EVs': [18, 9, 7, 24, 41, 11], 'Nature': 8, 'Stats': [77, 54, 72, 37, 56, 33], 'StatModifiers': [0, 0, 0, 0, 0, 0, 0, 0, 0], 'StatusEffects': 0, 'CurrentHP': 67, 'HeldItem': {'Id': 0, 'Name': '', 'Category': 0, 'FlingPower': 0, 'FlingEffect': 0, 'Flags': 0}, 'Moves': [{'Id': 18, 'CurrentPP': 19, 'MaxPP': 20, 'Name': 'Whirlwind', 'Type': 1, 'Category': 0, 'Targets': 10, 'Priority': -6, 'Power': 0, 'Accuracy': 0, 'InitialMaxPP': 20, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 0, 'Flags': 264193, 'AffectedStat': 0, 'StatStages': 0}, {'Id': 242, 'CurrentPP': 15, 'MaxPP': 15, 'Name': 'Crunch', 'Type': 65536, 'Category': 1, 'Targets': 10, 'Priority': 0, 'Power': 80, 'Accuracy': 100, 'InitialMaxPP': 15, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 20, 'Flags': 18452, 'AffectedStat': 2, 'StatStages': -1}, {'Id': 61, 'CurrentPP': 20, 'MaxPP': 20, 'Name': 'Bubble Beam', 'Type': 1024, 'Category': 2, 'Targets': 10, 'Priority': 0, 'Power': 65, 'Accuracy': 100, 'InitialMaxPP': 20, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 10, 'Flags': 18432, 'AffectedStat': 5, 'StatStages': -1}, {'Id': 457, 'CurrentPP': 5, 'MaxPP': 5, 'Name': 'Head Smash', 'Type': 32, 'Category': 1, 'Targets': 10, 'Priority': 0, 'Power': 150, 'Accuracy': 80, 'InitialMaxPP': 5, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': -50, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 0, 'Flags': 18448, 'AffectedStat': 0, 'StatStages': 0}], 'Friendship': 0, 'OriginalTrainerID': 0, 'Type': 16}}, 'Target': {'Party': 0, 'Slot': 0, 'Team': 0, 'Pokemon': {'Name': 'Pichu', 'NatDex': 172, 'Level': 30, 'Ability': 98, 'TotalExperience': 27000, 'Gender': 0, 'IVs': [0, 1, 2, 4, 0, 2], 'EVs': [13, 18, 17, 22, 32, 21], 'Nature': 8, 'Stats': [52, 30, 15, 28, 28, 43], 'StatModifiers': [0, 0, 0, 0, 0, 0, 0, 0, 0], 'StatusEffects': 0, 'CurrentHP': 52, 'HeldItem': {'Id': 0, 'Name': '', 'Category': 0, 'FlingPower': 0, 'FlingEffect': 0, 'Flags': 0}, 'Moves': [{'Id': 193, 'CurrentPP': 40, 'MaxPP': 40, 'Name': 'Foresight', 'Type': 1, 'Category': 0, 'Targets': 10, 'Priority': 0, 'Power': 0, 'Accuracy': 0, 'InitialMaxPP': 40, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 0, 'Flags': 280577, 'AffectedStat': 0, 'StatStages': 0}, {'Id': 433, 'CurrentPP': 5, 'MaxPP': 5, 'Name': 'Trick Room', 'Type': 8192, 'Category': 0, 'Targets': 12, 'Priority': -7, 'Power': 0, 'Accuracy': 0, 'InitialMaxPP': 5, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 0, 'Flags': 2048, 'AffectedStat': 0, 'StatStages': 0}, {'Id': 225, 'CurrentPP': 19, 'MaxPP': 20, 'Name': 'Dragon Breath', 'Type': 32768, 'Category': 2, 'Targets': 10, 'Priority': 0, 'Power': 60, 'Accuracy': 100, 'InitialMaxPP': 20, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 30, 'FlinchChance': 0, 'StatChance': 0, 'Flags': 18432, 'AffectedStat': 0, 'StatStages': 0}, {'Id': 232, 'CurrentPP': 35, 'MaxPP': 35, 'Name': 'Metal Claw', 'Type': 256, 'Category': 1, 'Targets': 10, 'Priority': 0, 'Power': 50, 'Accuracy': 95, 'InitialMaxPP': 35, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 10, 'Flags': 18448, 'AffectedStat': 1, 'StatStages': 1}], 'Friendship': 0, 'OriginalTrainerID': 0, 'Type': 4096}}, 'Move': {'Id': 18, 'CurrentPP': 19, 'MaxPP': 20, 'Name': 'Whirlwind', 'Type': 1, 'Category': 0, 'Targets': 10, 'Priority': -6, 'Power': 0, 'Accuracy': 0, 'InitialMaxPP': 20, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 0, 'Flags': 264193, 'AffectedStat': 0, 'StatStages': 0}}),
	Transaction(type=5, name="PPTransaction", args={'Move': {'Id': 18, 'CurrentPP': 19, 'MaxPP': 20, 'Name': 'Whirlwind', 'Type': 1, 'Category': 0, 'Targets': 10, 'Priority': -6, 'Power': 0, 'Accuracy': 0, 'InitialMaxPP': 20, 'MinHits': 0, 'MaxHits': 0, 'MinTurns': 0, 'MaxTurns': 0, 'Drain': 0, 'Healing': 0, 'CritRate': 0, 'AilmentChance': 0, 'FlinchChance': 0, 'StatChance': 0, 'Flags': 264193, 'AffectedStat': 0, 'StatStages': 0}, 'Amount': -1}),
	]
	)
)
# yapf: enable


class TestOtherHelpers(unittest.TestCase):

	@given(st.lists(garbage_transactions))
	def test_prettify_all_transactions_text_should_remain_in_bounds(self, transactions):
		pretty_texts = util.prettify_all_transactions(transactions)
		for text in pretty_texts:
			self.assertLessEqual(len(text), 2048)

	@given(st.lists(garbage_transactions))
	def test_prettify_all_transactions_should_never_contain_empty_string(
		self, transactions
	):
		pretty_texts = util.prettify_all_transactions(transactions)
		for text in pretty_texts:
			self.assertIsNotNone(text)
			self.assertIsInstance(text, str)
			self.assertNotEqual(text, "")


if __name__ == "__main__":
	unittest.main()
