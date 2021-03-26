import json

class Team():
	"""
	Represents a list of parties of pokemon.
	"""
	def __init__(self, **kwargs):
		self.parties: list[Party] = kwargs.pop("parties")

	# def toJSON(self) -> str:
	# 	json.dumps(self, default=lambda o: o.__dict__)

class Party():
	"""
	Represents a party of pokemon.
	"""
	def __init__(self, **kwargs):
		self.pokemon: list[Pokemon] = kwargs.pop("pokemon")

	# def toJSON(self) -> str:
	# 	json.dumps(self, default=lambda o: o.__dict__)

class Pokemon():
	pass

class BattleContext():
	"""This is a class that describes the point of view of a given Pokemon on the battlefield. It provides
	enough information for a user to make an informed decision about what turn to make next.   
	"""
	# will add make the docstrings comply with the sphinx format once this class is looking good

	def __init__(self):
		with open('data.json') as d:
			data = json.load(d)

		self.battle = data['Battle']
		self.pokemon = data['Pokemon']
		self.team = data['Team']
		self.targets = data['Targets']
		self.allies = data['Allies']
		self.opponents = data['Opponents']