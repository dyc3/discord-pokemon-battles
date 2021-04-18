import json
from typing import Any, Optional, Union, overload
import logging

log = logging.getLogger(__name__)


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

	def get_args(self) -> dict[str, Any]:
		"""Get the turn's parameters."""
		return {}

	def __repr__(self) -> str:
		return f"{type(self)}<{self.get_args()}>"


class FightTurn(Turn):
	"""Use a Pokemon's move."""

	TurnType = 0

	def __init__(self, **kwargs) -> None:
		self.target = {
			"Party": kwargs.pop("party"),
			"Slot": kwargs.pop("slot"),
		}
		self.move = kwargs.pop("move")

	def get_args(self) -> dict[str, Any]:
		"""Get the turn's parameters."""
		return {"Target": self.target, "move": self.move}


class ItemTurn(Turn):
	"""Use an item."""

	TurnType = 1

	def __init__(self, **kwargs) -> None:
		pass

	def get_args(self) -> dict[str, Any]:
		"""Get the turn's parameters."""
		return {}


class SwitchTurn(Turn):
	"""Switch a Pokemon out for another Pokemon."""

	TurnType = 2

	def __init__(self, **kwargs) -> None:
		pass

	def get_args(self) -> dict[str, Any]:
		"""Get the turn's parameters."""
		return {}


class RunTurn(Turn):
	"""Attempt to run away from the battle."""

	TurnType = 3

	def __init__(self, **kwargs) -> None:
		pass

	def get_args(self) -> dict[str, Any]:
		"""Get the turn's parameters."""
		return {}
