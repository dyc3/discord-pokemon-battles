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
