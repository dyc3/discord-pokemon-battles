import json

class Turn():
	type = None

	def __init__(self) -> None:
		pass

	def toJSON(self) -> str:
		return json.dumps({
			"type": type,
			"args": self,
		})

class FightTurn(Turn):
	type = 0

	def __init__(self, **kwargs) -> None:
		self.target = {
			"party": kwargs.pop("party"),
			"slot": kwargs.pop("slot"),
		}
		self.move = kwargs.pop("move")

class ItemTurn(Turn):
	type = 1

	def __init__(self, **kwargs) -> None:
		pass

class SwitchTurn(Turn):
	type = 2

	def __init__(self, **kwargs) -> None:
		pass

class RunTurn(Turn):
	type = 3

	def __init__(self, **kwargs) -> None:
		pass
