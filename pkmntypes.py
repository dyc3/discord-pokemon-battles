import json
from dataclasses import dataclass
from typing import Any, Optional
import logging


def _case_insensitive_pop(
	kwargs: dict[str, Any], name: str, default: Optional[Any] = None
) -> Any:
	if name in kwargs:
		return kwargs.pop(name)
	if name.lower() in kwargs:
		return kwargs.pop(name.lower())
	if default != None:
		return default
	raise KeyError(name)


@dataclass(init=False, repr=False)
class Pokemon():
	"""A Pokemon.

	FIXME: make all props snake case

	:param Name: The name of the Pokemon
	:param NatDex: The National Pokedex number for the Pokemon
	:param Level: The Pokemon's level
	:param Ability: The Pokemon's ability
	:param TotalExperience: The total amount of experience points gained by the Pokemon
	:param Gender: The Pokemon's gender
	:param IVs: The individual values for the Pokemon in an array that represent HP, Attack, Defense, Special Attack, Special Defense, and Speed
	:param EVs: The effort values associated with the Pokemon
	:param Nature: The Pokemon's nature represented by a value
	:param Stats: The stats for the Pokemon
	:param StatModifiers: The stat modifiers that could affect the Pokemon's stats
	:param StatusEffects: The value representing if the Pokemon has an status effects on it
	:param CurrentHP: The amount of health the Pokemon has
	:param HeldItem: Any item the Pokemon may be holding
	:param Moves: The move set of the Pokemon
	:param Friendship: A value representing the friendship of the Pokemon
	:param OriginalTrainerID: The ID of the trainer of the Pokemon
	:param Type: The type of Pokemon
	"""

	Name: str
	NatDex: int
	Level: int
	Ability: int
	TotalExperience: int
	Gender: int
	IVs: list[int]
	EVs: list[int]
	Nature: int
	Stats: list[int]
	StatModifiers: list[int]
	StatusEffects: int
	CurrentHP: int
	HeldItem: dict
	Moves: list[dict]
	Friendship: int
	OriginalTrainerID: int
	Type: int

	def __init__(self, **kwargs):
		if len(kwargs) == 0:
			return
		self.Name: str = _case_insensitive_pop(kwargs, 'Name')
		self.NatDex: int = _case_insensitive_pop(kwargs, 'NatDex')
		self.Level: int = _case_insensitive_pop(kwargs, 'Level')
		self.Ability: int = _case_insensitive_pop(kwargs, 'Ability')
		self.TotalExperience: int = _case_insensitive_pop(kwargs, 'TotalExperience')
		self.Gender: int = _case_insensitive_pop(kwargs, 'Gender')
		self.IVs: list[int] = _case_insensitive_pop(kwargs, 'IVs')
		self.EVs: list[int] = _case_insensitive_pop(kwargs, 'EVs')
		self.Nature: int = _case_insensitive_pop(kwargs, 'Nature')
		self.Stats: list[int] = _case_insensitive_pop(kwargs, 'Stats')
		self.StatModifiers: list[int] = _case_insensitive_pop(kwargs, 'StatModifiers')
		self.StatusEffects: int = _case_insensitive_pop(kwargs, 'StatusEffects')
		self.CurrentHP: int = _case_insensitive_pop(kwargs, 'CurrentHP')
		self.HeldItem: dict = _case_insensitive_pop(kwargs, 'HeldItem')
		self.Moves: list[dict] = _case_insensitive_pop(kwargs, 'Moves')
		self.Friendship: int = _case_insensitive_pop(kwargs, 'Friendship')
		self.OriginalTrainerID: int = _case_insensitive_pop(kwargs, 'OriginalTrainerID')
		self.Type: int = _case_insensitive_pop(kwargs, 'Type')


@dataclass
class Party():
	"""Represents a party of pokemon."""

	pokemon: list[Pokemon]


@dataclass
class Team():
	"""Represents a list of parties of pokemon."""

	parties: list[Party]


@dataclass(init=False)
class Target():
	"""Represents a target identified by it's party and slot."""

	party: int
	slot: int
	team: int
	pokemon: Pokemon

	def __init__(self, **kwargs):
		self.party: int = _case_insensitive_pop(kwargs, "Party", -1)
		self.slot: int = _case_insensitive_pop(kwargs, "Slot", -1)
		self.team: int = _case_insensitive_pop(kwargs, "Team", -1)
		self.pokemon: Pokemon = Pokemon(
			**_case_insensitive_pop(kwargs, "Pokemon")
		) if "Pokemon" in kwargs or "pokemon" in kwargs else None


@dataclass(init=False)
class BattleContext():
	"""Describes the point of view of a given Pokemon on the battlefield. It provides enough information for a user to make an informed decision about what turn to make next.

	:param battle: The state of the battlefield
	:param pokemon: The pokemon that this context belongs to
	:param team: The team ID of the `Pokemon`
	:param targets: All pokemon on the battlefield
	:param allies: Ally targets in relation to the `Pokemon`
	:param opponents: Enemy targets in relation to the `Pokemon`
	"""

	battle: dict
	pokemon: Pokemon
	team: int
	targets: list[Target]
	allies: list[Target]
	opponents: list[Target]

	def __init__(self, **kwargs):
		self.battle: dict = _case_insensitive_pop(kwargs, 'Battle')
		self.pokemon: Pokemon = Pokemon(**_case_insensitive_pop(kwargs, 'Pokemon'))
		self.team: int = _case_insensitive_pop(kwargs, 'Team')
		self.targets: list[Target] = [
			Target(**d) for d in _case_insensitive_pop(kwargs, 'Targets', [])
		]
		self.allies: list[Target] = [
			Target(**d) for d in _case_insensitive_pop(kwargs, 'Allies', [])
		]
		self.opponents: list[Target] = [
			Target(**d) for d in _case_insensitive_pop(kwargs, 'Opponents', [])
		]


class Transaction:
	"""Describes something that happened during a battle."""

	def __init__(self, **kwargs):
		self.type: int = kwargs["type"]
		self.name: str = kwargs["name"]
		self.args: dict[str, Any] = kwargs["args"]

	def pretty(self) -> str:
		"""Get a human-readable representation of this transaction."""
		if self.type == 0:
			user = Pokemon(**self.args["User"])
			target = Target(**self.args["Target"])
			move = self.args["Move"]

			return f"{user.Name} used {move['Name']} on {target.pokemon.Name} for {self.args['Damage']} damage."
		elif self.type == 8:
			target = Target(**self.args["Target"])

			return f"{target.pokemon.Name} fainted."
		elif self.type == 11:
			return f"The battle has ended."
		else:
			return f"TODO: {self.name}<{self.type}> {self.args}"
