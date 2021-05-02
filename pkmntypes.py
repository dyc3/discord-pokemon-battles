import logging, coloredlogs
import json
from dataclasses import dataclass
from typing import Any, Optional
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession
from PIL import Image
from enum import Enum, IntEnum
from pathlib import Path

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=log)


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

	_id: Optional[ObjectId]
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
	HeldItem: dict[str, Any]
	Moves: list[dict[str, Any]]
	Friendship: int
	OriginalTrainerID: int
	Type: int

	def __init__(self, **kwargs):
		if "_id" in kwargs:
			self._id = kwargs.pop("_id")
		else:
			self._id = kwargs.pop("id", None)
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

	async def save(self, session: AsyncIOMotorClientSession = None):
		"""Alias for `storage.save_object(pokemon)`."""
		import storage # avoid circular import
		await storage.save_object(self, session=session)

	def get_image(self) -> Image:
		"""Get the image of the pokemon."""
		return Image.open(f"./images/{self.NatDex}.png")

	def get_silhouette(self) -> Path:
		"""Return the path to the silhouette image of a pokemon. If the image doesn't exist it will be created.

		:returns: Path to pokemon silhouette
		"""
		imgPath = Path(f"./images/{self.NatDex}.png")
		silPath = Path(f"./images/{self.NatDex}_sil.png")
		if not silPath.exists():
			img = Image.open(imgPath)
			img = img.convert("RGBA")
			background = Image.open(f"./images/background.png")
			pixdata = img.load()

			width, height = img.size
			for y in range(height):
				for x in range(width):
					if pixdata[x, y][3] != 0:
						pixdata[x, y] = (0, 0, 0, 255)

			background.paste(img, (60, 60), img)
			background.save(silPath, "PNG")

		return silPath

	@property
	def name_and_type(self):
		"""Pretty print the pokemon's name and type, using emoji if possible."""
		import util
		return f"{self.Name} {util.safe_display_types(self.Type)}"


@dataclass(init=False)
class Party():
	"""Represents a party of pokemon."""

	pokemon: list[Pokemon]

	def __init__(self, **kwargs):
		self.pokemon = [
			pkmn if isinstance(pkmn, Pokemon) else Pokemon(**pkmn)
			for pkmn in _case_insensitive_pop(kwargs, "pokemon", [])
		]


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

	battle: dict[str, Any]
	pokemon: Pokemon
	team: int
	targets: list[Target]
	allies: list[Target]
	opponents: list[Target]

	def __init__(self, **kwargs):
		self.battle: dict[str, Any] = _case_insensitive_pop(kwargs, 'Battle')
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


class MoveFailReason(IntEnum):
	"""Reasons that a Pokemon's move could fail."""

	other = 0
	miss = 1
	dodge = 2


class Stat(IntEnum):
	"""Stats that a pokemon can have."""

	Hp = 0
	Attack = 1
	Defense = 2
	SpAttack = 3
	SpDefense = 4
	Speed = 5
	CritChance = 6
	Accuracy = 7
	Evasion = 8

	def __str__(self):
		if self == Stat.Hp:
			return "HP"
		elif self == Stat.Attack:
			return "Attack"
		elif self == Stat.Defense:
			return "Defense"
		elif self == Stat.SpAttack:
			return "SpAttack"
		elif self == Stat.SpDefense:
			return "SpDefense"
		elif self == Stat.Speed:
			return "Speed"
		elif self == Stat.CritChance:
			return "Crit Chance"
		elif self == Stat.Accuracy:
			return "Accuracy"
		elif self == Stat.Evasion:
			return "Evasion"


class Transaction:
	"""Describes something that happened during a battle."""

	def __init__(self, **kwargs):
		self.type: int = kwargs["type"]
		self.name: str = kwargs["name"]
		self.args: dict[str, Any] = kwargs["args"]

	def pretty(self) -> str:
		"""Get a human-readable representation of this transaction."""
		import util

		try:
			if self.name == "DamageTransaction":
				target = Target(**self.args["Target"])
				move = self.args["Move"]
				status = self.args["StatusEffect"]

				text = f"{target.pokemon.name_and_type} took {self.args['Damage']} damage."
				if status != 0:
					return text[:-1
								] + f" from {list(util.status_to_string(self.args['StatusEffect']))[0]}."
				else:
					return text
			elif self.name == "FriendshipTransaction":
				pkmn = Pokemon(**self.args["Target"])

				if self.args['Amount'] > 0:
					return f"{pkmn.name_and_type} friendship increased by {self.args['Amount']}."
				else:
					return f"{pkmn.name_and_type} friendship decreased by {abs(self.args['Amount'])}."
			elif self.name == "EVTransaction":
				pkmn = Pokemon(**self.args["Target"])
				stat = Stat(self.args['Stat'])

				return f"{pkmn.name_and_type} gained {self.args['Amount']} {stat} EVs."
			elif self.name == "HealTransaction":
				pkmn = Pokemon(**self.args["Target"])

				return f"{pkmn.name_and_type} restored {self.args['Amount']} HP."
			elif self.name == "InflictStatusTransaction":
				pkmn = Pokemon(**self.args["Target"])

				return f"{pkmn.name_and_type} was {list(util.status_to_string(self.args['StatusEffect']))[0]}."
			elif self.name == "FaintTransaction":
				target = Target(**self.args["Target"])

				return f"{target.pokemon.Name} fainted."
			elif self.name == "EndBattleTransaction":
				return f"The battle has ended."
			elif self.name == "MoveFailTransaction":
				user = Pokemon(**self.args["User"])
				reason = MoveFailReason(self.args["Reason"])

				msg = "failed"
				if reason == MoveFailReason.miss:
					msg = "missed"
				elif reason == MoveFailReason.dodge:
					msg = "was dodged"
				return f"{user.name_and_type} {msg}."
			elif self.name == "ModifyStatTransaction":
				pkmn = Pokemon(**self.args["Target"])
				stat = Stat(self.args['Stat'])
				stages = self.args['Stages']

				if stages > 0:
					direc = "increased"
				else:
					direc = "decreased"
				return f"{pkmn.name_and_type}'s {stat} {direc} by {abs(stages)}."
			elif self.name == "PPTransaction":
				move = self.args["Move"]
				if self.args["Amount"] > 0:
					return f"{move['Name']} restored {self.args['Amount']} PP."
				else:
					return f"{move['Name']} lost {abs(self.args['Amount'])} PP."
			elif self.name == "UseMoveTransaction":
				tuser = Target(**self.args["User"])
				target = Target(**self.args["Target"])
				move = self.args["Move"]
				return f"{tuser.pokemon.name_and_type} used {move['Name']} on {target.pokemon.name_and_type}!"
			elif self.name == "SendOutTransaction":
				target = Target(**self.args["Target"])
				return f"{target.pokemon.name_and_type} was sent out."
			elif self.name == "ImmobilizeTransaction":
				target = Target(**self.args["Target"])
				status = self.args["StatusEffect"]
				return f"{target.pokemon.name_and_type} is {util.status_to_string(status)}!"
			elif self.name == "CureStatusTransaction":
				target = Target(**self.args["Target"])
				status = self.args["StatusEffect"]
				return f"{target.pokemon.name_and_type} is no longer {util.status_to_string(status)}!"
			elif self.name == "WeatherTransaction":
				weather = BattleWeather(self.args["Weather"])
				if weather == BattleWeather.ClearSkies:
					return "The weather is now **clear**."
				elif weather == BattleWeather.HarshSunlight:
					return "The **sunlight turned harsh**."
				elif weather == BattleWeather.Rain:
					return "It started to **rain**."
				elif weather == BattleWeather.Sandstorm:
					return "A **sandstorm** brewed."
				elif weather == BattleWeather.Hail:
					return "It started to **hail**."
				elif weather == BattleWeather.Fog:
					return "The **fog** is deep..."
				else:
					return f"The weather is now **{weather}**."
			else:
				return f"TODO: {self.name}<{self.type}> {self.args}"
		except Exception as e:
			log.error(f"Failed to pretty print transaction: {type(e)} {e}")
			return f"Failed: {self.name}<{self.type}> {self.args}"

	def __repr__(self):
		return f'Transaction(type={self.type}, name="{self.name}", args={self.args})'


TYPE_ELEMENTS = [
	"Normal",
	"Fighting",
	"Flying",
	"Poison",
	"Ground",
	"Rock",
	"Bug",
	"Ghost",
	"Steel",
	"Fire",
	"Water",
	"Grass",
	"Electric",
	"Psychic",
	"Ice",
	"Dragon",
	"Dark",
]


class BattleWeather(Enum):
	"""Weather conditions that can be present on the battlefield."""

	ClearSkies = 0
	HarshSunlight = 1
	Rain = 2
	Sandstorm = 3
	Hail = 4
	Fog = 5
