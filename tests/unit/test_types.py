import unittest
from turns import *
import json
from pkmntypes import *
from hypothesis import given, reproduce_failure, strategies as st

status_condition_strategy = st.builds(
	StatusCondition,
	non_volatile=st.sampled_from(StatusCondition.NonVolatile),
	volatile=st.sampled_from(StatusCondition.Volatile)
)


class TestPkmnTypes(unittest.TestCase):

	def test_pokemon(self):
		data = json.loads(
			'{"Name":"Regigigas","NatDex":486,"Level":14,"Ability":89,"TotalExperience":3430,"Gender":0,"IVs":[1,3,0,2,4,3],"EVs":[27,40,6,41,4,7],"Nature":8,"Stats":[55,51,35,29,36,33],"StatModifiers":[0,0,0,0,0,0,0,0,0],"StatusEffects":0,"CurrentHP":55,"HeldItem":{"Id":0,"Name":"","Category":0,"FlingPower":0,"FlingEffect":0,"Flags":0},"Moves":[{"Id":33,"CurrentPP":0,"MaxPP":0,"Name":"Tackle","Type":1,"Category":1,"Targets":10,"Priority":0,"Power":40,"Accuracy":100,"InitialMaxPP":0},{"Id":205,"CurrentPP":0,"MaxPP":0,"Name":"Rollout","Type":32,"Category":1,"Targets":10,"Priority":0,"Power":30,"Accuracy":90,"InitialMaxPP":0},{"Id":408,"CurrentPP":0,"MaxPP":0,"Name":"Power Gem","Type":32,"Category":2,"Targets":10,"Priority":0,"Power":80,"Accuracy":100,"InitialMaxPP":0},{"Id":288,"CurrentPP":0,"MaxPP":0,"Name":"Grudge","Type":128,"Category":0,"Targets":7,"Priority":0,"Power":0,"Accuracy":0,"InitialMaxPP":0}],"Friendship":0,"OriginalTrainerID":0,"Type":1}'
		)
		pkmn = Pokemon(**data)
		self.assertEqual(pkmn.Name, "Regigigas")
		self.assertEqual(pkmn.NatDex, 486)
		self.assertEqual(pkmn.Level, 14)
		self.assertEqual(len(pkmn.Moves), 4)
		self.assertEqual(type(pkmn.Moves[0]), Move)
		self.assertEqual(pkmn.Moves[0].name, "Tackle")

	def test_move(self):
		data = json.loads(
			'{"Id":1,"Name": "Pound","Type": 1,"Category": 1,"Targets": 10,"Priority": 0,"Power": 40,"Accuracy": 100,"InitialMaxPP": 35,"MinHits": 0,"MaxHits": 0,"MinTurns": 0,"MaxTurns": 0,"Drain": 0,"Healing": 0,"CritRate": 0,"AilmentChance": 0,"FlinchChance": 0,"StatChance": 0,"Flags": 18448,"AffectedStat": 0,"StatStages": 0,"Ailment": 0}'
		)
		move = Move(**data)
		self.assertEqual(move.move_id, 1)
		self.assertEqual(move.name, "Pound")

	@given(status_condition_strategy)
	def test_status_condition_parse(self, status: StatusCondition):
		self.assertEqual(status.value, StatusCondition(status.value).value)

	@given(status_condition_strategy)
	def test_status_condition_past_tense(self, status: StatusCondition):
		self.assertFalse(status.past_tense.startswith(","))
		self.assertFalse(status.past_tense.endswith(","))

	@given(status_condition_strategy)
	def test_status_condition_past_tense_no_enum_types(self, status: StatusCondition):
		self.assertFalse("Volatile" in status.past_tense)
		self.assertFalse("NonVolatile" in status.past_tense)


if __name__ == "__main__":
	unittest.main()
