import json
from typing import Optional, Union

class Turn():
	TurnType: Optional[int] = None

	def __init__(self) -> None:
		pass

	def toJSON(self) -> str:
		return json.dumps({
			"type": self.TurnType,
			"args": self.get_args(),
		})

	def get_args(self):
		return {}

class FightTurn(Turn):
	TurnType = 0

	def __init__(self, **kwargs) -> None:
		self.target = {
			"party": kwargs.pop("party"),
			"slot": kwargs.pop("slot"),
		}
		self.move = kwargs.pop("move")

	def get_args(self):
		return {
			"target": self.target,
			"move": self.move
		}

class ItemTurn(Turn):
	TurnType = 1

	def __init__(self, **kwargs) -> None:
		pass

	def get_args(self):
		return {}

class SwitchTurn(Turn):
	TurnType = 2

	def __init__(self, **kwargs) -> None:
		pass

	def get_args(self):
		return {}

class RunTurn(Turn):
	TurnType = 3

	def __init__(self, **kwargs) -> None:
		pass

	def get_args(self):
		return {}
