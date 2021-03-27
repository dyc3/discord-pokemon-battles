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

	:param battle: The state of the battlefield
	:param pokemon: The pokemon that this context belongs to
	:param team: The team ID of the `Pokemon`
	:param targets: All pokemon on the battlefield
	:param allies: Ally targets in relation to the `Pokemon`
	:param opponents: Enemy targets in relation to the `Pokemon`
	"""
	
	def __init__(self, **kwargs):
		self.battle: dict = kwargs['Battle']
		self.pokemon: dict = kwargs['Pokemon']
		self.team: dict = kwargs['Team']
		self.targets: dict = kwargs['Targets']
		self.allies: dict = kwargs['Allies']
		self.opponents: dict = kwargs['Opponents']