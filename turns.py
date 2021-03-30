import json
from typing import Optional, Union, overload


class Turn():
	"""Represents an :class:`Agent`'s turn."""

	TurnType: Optional[int] = None

	def __init__(self) -> None:
		pass

	def toJSON(self) -> str:
		"""Serialize the turn to submit to the battle API."""
		return json.dumps({
			"type": self.TurnType,
			"args": self.get_args(),
		})

	def get_args(self) -> dict:
		"""Get the turn's parameters."""
		return {}


class FightTurn(Turn):
	"""Use a Pokemon's move."""

	TurnType = 0

	def __init__(self, **kwargs) -> None:
		self.target = {
			"party": kwargs.pop("party"),
			"slot": kwargs.pop("slot"),
		}
		self.move = kwargs.pop("move")

	@overload
	def get_args(self):
		return {"target": self.target, "move": self.move}


class ItemTurn(Turn):
	"""Use an item."""

	TurnType = 1

	def __init__(self, **kwargs) -> None:
		pass

	@overload
	def get_args(self):
		return {}


class SwitchTurn(Turn):
	"""Switch a Pokemon out for another Pokemon."""

	TurnType = 2

	def __init__(self, **kwargs) -> None:
		pass

	@overload
	def get_args(self):
		return {}


class RunTurn(Turn):
	"""Attempt to run away from the battle."""

	TurnType = 3

	def __init__(self, **kwargs) -> None:
		pass

	@overload
	def get_args(self):
		return {}
