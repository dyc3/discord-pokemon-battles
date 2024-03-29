import logging, coloredlogs
from turns import FightTurn
from dataclasses import dataclass
from typing import Any, Optional
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession
from PIL import Image
from enum import Enum, IntEnum, IntFlag
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


__exclude_exports__ = set(dir())


@dataclass(init=False)
class StatusCondition():
	"""Pokmon status condition. Represented as a bit field."""

	class NonVolatile(IntEnum):
		"""Status conditions that drastically cripple a pokemon."""

		none = 0
		burn = 1
		freeze = 2
		paralyze = 3
		poison = 4
		badly_poison = 5
		sleep = 6

		def __str__(self):
			if self == self.none:
				return "none"
			elif self == self.burn:
				return "burn"
			elif self == self.freeze:
				return "freeze"
			elif self == self.paralyze:
				return "paralyze"
			elif self == self.poison:
				return "poison"
			elif self == self.badly_poison:
				return "badly_poison"
			elif self == self.sleep:
				return "sleep"

		@property
		def past_tense(self):
			"""Get the past tense form of this condition."""

			if self == self.burn:
				return "burned"
			elif self == self.freeze:
				return "frozen"
			elif self == self.paralyze:
				return "paralyzed"
			elif self == self.poison:
				return "poisoned"
			elif self == self.badly_poison:
				return "badly poisoned"
			elif self == self.sleep:
				return "asleep"
			else:
				return ""

		@property
		def emoji(self):
			"""Get the emoji for this condition."""
			ename = f"status{self.name}"
			import util
			if ename in util.emoji_cache:
				return util.emoji_cache[ename]

	class Volatile(IntFlag):
		"""Other status conditions."""

		none = 0
		bound = 1 << 0
		cant_escape = 1 << 1
		confusion = 1 << 2
		cursed = 1 << 3
		embargo = 1 << 4
		flinch = 1 << 5
		heal_block = 1 << 6
		identified = 1 << 7
		infatuation = 1 << 8
		leech_seed = 1 << 9
		nightmare = 1 << 10
		perish_song = 1 << 11
		taunt = 1 << 12
		torment = 1 << 13

		@property
		def past_tense(self):
			"""Get the past tense form of this condition."""

			conds = []
			for cond in type(self):
				if self & cond > 0:
					if self == self.bound:
						val = "bound"
					elif self == self.cant_escape:
						val = "can't escape"
					elif self == self.confusion:
						val = "confused"
					elif self == self.cursed:
						val = "cursed"
					elif self == self.embargo:
						val = "embargoed"
					elif self == self.flinch:
						val = "flinched"
					elif self == self.heal_block:
						val = "heal blocked"
					elif self == self.identified:
						val = "infatuated"
					elif self == self.infatuation:
						val = "identified"
					elif self == self.leech_seed:
						val = "leeched"
					elif self == self.nightmare:
						val = "nightmared"
					elif self == self.perish_song:
						val = "perished"
					elif self == self.taunt:
						val = "taunted"
					elif self == self.torment:
						val = "tormented"
					else:
						val = None
					if val:
						conds += [val]
			return ', '.join(conds)

	non_volatile: NonVolatile = NonVolatile.none
	volatile: Volatile = Volatile.none

	def __init__(self, value=None, *, non_volatile=None, volatile=None):
		assert not (value != None and (non_volatile != None or volatile != None))
		if value:
			self.__setstate__(value)
		if non_volatile:
			self.non_volatile = non_volatile
		if volatile:
			self.volatile = volatile

	@property
	def value(self) -> int:
		"""Get the combined value of this condition."""
		return int(self.non_volatile & (self.volatile << 3))

	def __getstate__(self):
		return self.value

	def __setstate__(self, value):
		if isinstance(value, StatusCondition):
			self.non_volatile = value.non_volatile
			self.volatile = value.volatile
		else:
			self.non_volatile = self.NonVolatile(value & 0b111)
			self.volatile = self.Volatile(value >> 3)

	def __eq__(self, other):
		return self.value == other

	@property
	def past_tense(self):
		"""Get the past tense form of this condition."""
		return ', '.join([self.non_volatile.past_tense,
							self.volatile.past_tense]).strip(', ')


@dataclass(init=False, repr=False)
class Move():
	"""A Pokemon's move."""

	move_id: int
	current_pp: int
	max_pp: int
	name: str
	elemental_type: int
	category: int
	targets: int
	priority: int
	power: int
	accuracy: int
	initial_max_pp: int
	min_hits: int
	max_hits: int
	min_turns: int
	max_turns: int
	drain: int
	healing: int
	crit_rate: int
	ailment_chance: int
	flinch_chance: int
	stat_chance: int
	flags: int
	affected_stat: int
	stat_stages: int
	ailment: StatusCondition
	meta_category: int

	json_fields = {
		"Id": "move_id",
		"CurrentPP": "current_pp",
		"MaxPP": "max_pp",
		"Name": "name",
		"Type": "elemental_type",
		"Category": "category",
		"Targets": "targets",
		"Priority": "priority",
		"Power": "power",
		"Accuracy": "accuracy",
		"InitialMaxPP": "initial_max_pp",
		"MinHits": "min_hits",
		"MaxHits": "max_hits",
		"MinTurns": "min_turns",
		"MaxTurns": "max_turns",
		"Drain": "drain",
		"Healing": "healing",
		"CritRate": "crit_rate",
		"AilmentChance": "ailment_chance",
		"FlinchChance": "flinch_chance",
		"StatChance": "stat_chance",
		"Flags": "flags",
		"AffectedStat": "affected_stat",
		"StatStages": "stat_stages",
		"Ailment": "ailment",
		"MetaCategory": "meta_category",
	}

	def __init__(self, **kwargs):
		import util
		util.json_parse(self, kwargs)

	def __getstate__(self):
		return {
			json_field: self.__getattribute__(attr)
			for json_field, attr in self.json_fields.items()
		}

	def __setstate__(self, d):
		import util
		util.json_parse(self, d)

	@property
	def name_and_type(self) -> str:
		"""Pretty print the move's name and type, using emoji if possible."""
		import util
		return f"{self.name} {util.safe_display_types(self.elemental_type)}"


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
	StatusEffects: StatusCondition
	CurrentHP: int
	HeldItem: dict[str, Any]
	Moves: list[Move]
	Friendship: int
	OriginalTrainerID: int
	Type: int

	json_fields = {
		"Name": "Name",
		"NatDex": "NatDex",
		"Level": "Level",
		"Ability": "Ability",
		"TotalExperience": "TotalExperience",
		"Gender": "Gender",
		"IVs": "IVs",
		"EVs": "EVs",
		"Nature": "Nature",
		"Stats": "Stats",
		"StatModifiers": "StatModifiers",
		"StatusEffects": "StatusEffects",
		"CurrentHP": "CurrentHP",
		"HeldItem": "HeldItem",
		"Moves": "Moves",
		"Friendship": "Friendship",
		"OriginalTrainerID": "OriginalTrainerID",
		"Type": "Type",
	}

	def __init__(self, **kwargs):
		if "_id" in kwargs:
			self._id = kwargs.pop("_id")
		else:
			self._id = kwargs.pop("id", None)
		import util
		util.json_parse(self, kwargs)

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

	json_fields = {
		"Party": "party",
		"Slot": "slot",
		"Team": "team",
		"Pokemon": "pokemon",
	}

	def __init__(self, **kwargs):
		import util
		util.json_parse(self, kwargs)


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
	target_pokemon: Target
	team: int
	targets: list[Target]
	allies: list[Target]
	opponents: list[Target]

	json_fields = {
		"Battle": "battle",
		"Self": "target_pokemon",
		"Team": "team",
		"Targets": "targets",
		"Allies": "allies",
		"Opponents": "opponents",
	}

	def __init__(self, **kwargs) -> None:
		import util
		util.json_parse(self, kwargs)

	@property
	def pokemon(self) -> Pokemon:
		"""Alias for `target_pokemon.pokemon`."""
		return self.target_pokemon.pokemon

	def fight(self, target: Target, move: Move) -> FightTurn:
		"""Create a :class:`FightTurn` a little bit easier."""
		return FightTurn(
			party=target.party, slot=target.slot, move=self.pokemon.Moves.index(move)
		)


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

	def pretty(self, context: list[Team]) -> str:
		"""Get a human-readable representation of this transaction."""
		import util
		try:
			if self.name == "DamageTransaction":
				target = util.resolve_target(context, Target(**self.args["Target"]))
				status = StatusCondition(self.args["StatusEffect"])

				text = f"{target.pokemon.name_and_type} took **{self.args['Damage']} damage**."
				if status != 0:
					return text[:-1] + f" from being {status.past_tense}."
				else:
					return text
			elif self.name == "FriendshipTransaction":
				pkmn = util.resolve_target(context, Target(**self.args["Target"])).pokemon

				if self.args['Amount'] > 0:
					return f"{pkmn.name_and_type} friendship increased by {self.args['Amount']}."
				else:
					return f"{pkmn.name_and_type} friendship decreased by {abs(self.args['Amount'])}."
			elif self.name == "EVTransaction":
				pkmn = util.resolve_target(context, Target(**self.args["Target"])).pokemon
				stat = Stat(self.args['Stat'])

				return f"{pkmn.name_and_type} gained {self.args['Amount']} {stat} EVs."
			elif self.name == "HealTransaction":
				pkmn = util.resolve_target(context, Target(**self.args["Target"])).pokemon

				return f"{pkmn.name_and_type} restored {self.args['Amount']} HP."
			elif self.name == "InflictStatusTransaction":
				pkmn = util.resolve_target(context, Target(**self.args["Target"])).pokemon
				status = StatusCondition(self.args["StatusEffect"])

				return f"{pkmn.name_and_type} was **{status.past_tense}**."
			elif self.name == "FaintTransaction":
				target = util.resolve_target(context, Target(**self.args["Target"]))

				return f"{target.pokemon.name_and_type} **fainted**."
			elif self.name == "EndBattleTransaction":
				return f"The battle has ended."
			elif self.name == "MoveFailTransaction":
				user = util.resolve_target(context, Target(**self.args["User"])).pokemon
				reason = MoveFailReason(self.args["Reason"])

				if reason == MoveFailReason.miss:
					msg = "**missed**"
				elif reason == MoveFailReason.dodge:
					msg = "was **dodged**"
				else:
					msg = "**failed**"
				return f"{user.name_and_type} {msg}."
			elif self.name == "ModifyStatTransaction":
				pkmn = util.resolve_target(context, Target(**self.args["Target"])).pokemon
				stat = Stat(self.args['Stat'])
				stages = self.args['Stages']

				if stages > 0:
					direc = "increased"
				else:
					direc = "decreased"
				return f"{pkmn.name_and_type}'s {stat} {direc} by {abs(stages)}."
			elif self.name == "PPTransaction":
				move = Move(**self.args["Move"])
				if self.args["Amount"] > 0:
					return f"{move.name_and_type} restored {self.args['Amount']} PP."
				else:
					return f"{move.name_and_type} lost {abs(self.args['Amount'])} PP."
			elif self.name == "UseMoveTransaction":
				tuser = util.resolve_target(context, Target(**self.args["User"]))
				target = util.resolve_target(context, Target(**self.args["Target"]))
				move = Move(**self.args["Move"])
				return f"{tuser.pokemon.name_and_type} used {move.name_and_type} on {target.pokemon.name_and_type}!"
			elif self.name == "SendOutTransaction":
				target = util.resolve_target(context, Target(**self.args["Target"]))
				return f"{target.pokemon.name_and_type} was sent out."
			elif self.name == "ImmobilizeTransaction":
				target = util.resolve_target(context, Target(**self.args["Target"]))
				status = StatusCondition(self.args["StatusEffect"])
				return f"{target.pokemon.name_and_type} is **{status.past_tense}**!"
			elif self.name == "CureStatusTransaction":
				target = util.resolve_target(context, Target(**self.args["Target"]))
				status = StatusCondition(self.args["StatusEffect"])
				return f"{target.pokemon.name_and_type} is no longer **{status.past_tense}**!"
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
					return f"The weather changed to **{weather}**."
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


#__all__ = [x for x in dir() if not x.startswith("_") or x not in __exclude_exports__]
__all__ = [
	"StatusCondition", "Move", "Pokemon", "Party", "Team", "Target", "Stat",
	"BattleContext", "MoveFailReason", "Transaction", "Stat", "TYPE_ELEMENTS",
	"BattleWeather"
] # HACK: because type checker can't parse dynamic __all__
