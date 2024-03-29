from typing import Generator, Iterable, Sequence, Union, Optional, Any
import logging, coloredlogs
import discord
import asyncio
from discord.ext import commands
from discord.message import Message
from turns import *
from pkmntypes import *

RESPONSE_REACTIONS = [
	"🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵"
]

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=log)


async def prompt_menu(
	bot: commands.Bot,
	user: discord.User,
	content: str,
	title: str,
	description: str,
	items: Sequence[Union[str, tuple[str, str]]],
	use_channel: Optional[discord.TextChannel] = None
):
	"""Create menu for the user to choose between several options."""

	if use_channel:
		channel = use_channel
	else:
		if not user.dm_channel:
			await user.create_dm()
		channel = user.dm_channel

	embed = discord.Embed(title=title, description=description)

	count = 0
	for item in items:
		name, value = None, None
		if isinstance(item, tuple):
			name, value = item
		else:
			name = item
		embed.add_field(
			name=f"{RESPONSE_REACTIONS[count]}: {name}",
			value=value if value else count,
			inline=False
		)
		count += 1

	msg: Message = await channel.send(content=content, embed=embed)
	for r in RESPONSE_REACTIONS[:len(items)]:
		bot.loop.create_task(msg.add_reaction(r))

	def check(payload):
		log.debug(f"checking payload {payload}")
		return payload.message_id == msg.id and payload.user_id == user.id and str(
			payload.emoji
		) in RESPONSE_REACTIONS

	try:
		log.debug("waiting for user's reaction")
		# HACK: reaction_add doesn't work in DMs
		payload = await bot.wait_for("raw_reaction_add", check=check)
	except asyncio.TimeoutError as e:
		await channel.send("timed out")
		raise e

	reactionId = RESPONSE_REACTIONS.index(str(payload.emoji))
	embed.clear_fields()
	reaction = [items[reactionId]]

	for item in reaction:
		name, value = None, None
		if isinstance(item, tuple):
			name, value = item
		else:
			name = item
		embed.add_field(name=name, value=value if value else "Selected", inline=False)

	await msg.edit(content="Selected", embed=embed)

	return reactionId


async def prompt_message(
	bot: commands.Bot, user: discord.User, msg: discord.Message, emojis: list[str]
):
	"""Works very similar to prompt_menu except it takes in the message and a list of reactions instead of the specific menu_items."""

	for r in emojis:
		bot.loop.create_task(msg.add_reaction(r))

	def check(payload):
		log.debug(f"checking payload {payload}")
		return payload.message_id == msg.id and payload.user_id == user.id and str(
			payload.emoji
		) in emojis

	try:
		log.debug("waiting for user's reaction")
		# HACK: reaction_add doesn't work in DMs
		payload = await bot.wait_for("raw_reaction_add", check=check)
	except asyncio.TimeoutError as e:
		log.error("timed out")
		raise e

	reactionId = emojis.index(str(payload.emoji))

	return reactionId


async def prompt_for_turn(
	bot: commands.Bot,
	user: discord.User,
	battlecontext: BattleContext,
	use_channel: Optional[discord.TextChannel] = None
) -> Turn:
	"""Prompt the given user for a turn.

	:param bot: The discord bot
	:param user: The discord user
	:param battlecontext: The :class:`BattleContext` that will be given to the user.
	:param use_channel: Override the channel that is used to communicate with the user. By default, it will use the user's :class:`discord.DMChannel` to send the prompt. Primarily used for tests.
	:returns: The turn that the user made.
	TODO: prompt user for what type of turn
	"""

	title = f"{battlecontext.pokemon.Name} {battlecontext.pokemon.StatusEffects.non_volatile.emoji or ''}"
	description = f"{battlecontext.pokemon.CurrentHP} HP {safe_display_types(battlecontext.pokemon.Type)}"
	content = "Select a move"

	menu_items = []
	for i, move in enumerate(battlecontext.pokemon.Moves):
		menu_items.append(
			(
				f"{move.name}",
				f"{safe_display_types(move.elemental_type)} {move.current_pp}/{move.max_pp}"
			)
		)

	moveId = await prompt_menu(
		bot, user, content, title, description, menu_items, use_channel
	)

	target = battlecontext.opponents[0]
	return FightTurn(party=target.party, slot=target.slot, move=moveId)


def status_to_string(status: Union[int, StatusCondition]) -> set[str]:
	"""Get the human-readbale form of a Pokemon's Status Condition.

	:param status: pokemon battle status as defined in pokemonbattlelib
	:raises ValueError: raised if `status` is not of the proper format
	:return: a set of status name strings
	"""

	if isinstance(status, StatusCondition):
		status = status.value

	nonvolatile = [
		"None",
		"Burn",
		"Freeze",
		"Paralyze",
		"Poison",
		"BadlyPoison",
		"Sleep",
	]
	volatile = [
		"Bound",
		"CantEscape",
		"Confusion",
		"Cursed",
		"Embargo",
		"Flinch",
		"HealBlock",
		"Identified",
		"Infatuation",
		"LeechSeed",
		"Nightmare",
		"PerishSong",
		"Taunt",
		"Torment",
	]

	try:
		bitmask = status & ((1 << 3) - 1)
		if bitmask != 0:
			nonvolatile = [nonvolatile[bitmask]]
		else:
			nonvolatile = []

		bitmask = status >> 3
		volatile = [
			flag for (index, flag) in enumerate(volatile) if (bitmask & 1 << index)
		]
		return set(nonvolatile + volatile)
	except IndexError:
		raise ValueError("invalid value for status")


def type_to_string(elemental_type: int) -> set[str]:
	"""Convert a bit mask of elemental types to human readable strings.

	:param elemental_type: A bit mask of elemental types.
	:returns: A set of all elemental types indicated by the bit mask.
	"""

	return set(
		[
			flag for (index, flag) in enumerate(TYPE_ELEMENTS)
			if (elemental_type & 1 << index)
		]
	)


def type_emoji_name(t: str) -> str:
	"""Get the name of the emoji associated with the given type."""
	return f"type{t.lower()}"


emoji_cache: dict[str, discord.Emoji] = {}


def cache_emoji(emoji: discord.Emoji):
	"""Add the given emoji to a global cache so we can access them later without a reference to `bot`."""
	global emoji_cache
	if emoji.name not in emoji_cache:
		log.debug(f"Adding emoji {emoji.name} to cache")
		emoji_cache[emoji.name] = emoji


def safe_display_types(elemental_type: int) -> str:
	"""Use custom emojis to display the types, if available. Otherwise, just use strings."""
	types = sorted(type_to_string(elemental_type))
	combined = []
	for text in types:
		combined += [
			emoji_cache[ename] if
			(ename := type_emoji_name(text)) in emoji_cache else f"[{text}]"
		]

	return ' '.join(map(str, combined))


def build_teams_single(*parties: Union[Party, list[Pokemon]]) -> list[Team]:
	"""Take 2 parties of pokemon, creates a list of teams suitable to create a single battle.

	:returns: List of teams with 1 party each.
	"""
	assert len(parties) == 2, "must be given 2 parties"
	teams = []
	for party in parties:
		if isinstance(party, Party):
			team = Team(parties=[party])
		else:
			team = Team(parties=[Party(pokemon=party)])
		teams += [team]
	return teams


def taggify(s: Iterable[str]) -> str:
	"""Pretty print the outputs from `status_to_string` and `type_to_string`, surounding each item with square brackets.

	:returns: A prettier representation.
	"""
	return ''.join([f'[{x}]' for x in s])


def prettify_all_transactions(transactions: list[Transaction],
								context: list[Team]) -> list[str]:
	"""Prettify all transactions, and concatenate/truncate them such that they fit inside the description of a :class:`discord.Embed`.

	:param transactions: The list of transactions to prettify.
	"""
	return strings_to_embed_text([t.pretty(context) for t in transactions])


def strings_to_embed_text(strings: list[str]) -> list[str]:
	"""Concatenate/truncate a list of strings such that they fit inside the description of a :class:`discord.Embed`."""
	texts = []
	current = ""
	char_limit = 2048
	while len(strings) > 0:
		value = strings.pop(0)
		if len(current) + len(value) + 1 > char_limit:
			if len(current) > 0:
				texts += [current]
			if len(value) > char_limit:
				texts += [value[:char_limit]]
				continue
			current = ""
		current += value + "\n"
	if len(current) > 0:
		texts += [current]
	return texts


def get_link(msg: Message):
	"""Get the direct link for a message."""
	return f"https://discord.com/channels/{msg.guild.id}/{msg.channel.id}/{msg.id}"


def json_parse(self, kwargs: dict[str, Any]):
	"""Parse json dicts into the correct object according to type annotations."""
	assert self.json_fields, f"{type(self)} does not have a json_fields attribute."
	assert isinstance(
		self.json_fields, dict
	), f"json_fields must be a dict, got ({type(self.json_fields)} instead)"

	def parse_obj(attr_type, obj):
		try:
			if isinstance(obj, list):
				item_type = attr_type.__args__[0]
				value = [parse_obj(item_type, i) for i in obj if i != None]
			else:
				if isinstance(obj, dict):
					value = attr_type(**obj)
				else:
					value = attr_type(obj)
			return value
		except Exception as e:
			raise Exception(
				f"Error when parsing: attr_type={attr_type}, obj type={type(obj)}, obj={obj}"
			) from e

	for k, v in kwargs.items():
		if k in self.json_fields:
			attr_type = self.__annotations__[self.json_fields[k]]
			attr_value = parse_obj(attr_type, v)
			self.__setattr__(self.json_fields[k], attr_value)
			assert self.json_fields[k] in self.__dict__
		elif k in self.__annotations__:
			self.__setattr__(k, v)
		else:
			raise KeyError(f"Unknown keyword argument: {k}")


def resolve_target(teams: list[Team], target: Target) -> Target:
	"""Return `target` with the `pokemon` field populated according to the party and slot in `teams`."""
	parties = []
	for team in teams:
		for party in team.parties:
			parties.append(party)
	target.pokemon = parties[target.party].pokemon[target.slot]
	return target
