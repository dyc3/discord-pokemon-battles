import logging, coloredlogs
import discord
import asyncio
from discord.ext import commands
from discord.message import Message
from turns import *
from typing import Iterable, Sequence, Union
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
	bot: commands.Bot, user: discord.User, msg: discord.Message, list_of_emojis: list[str]
):
	"""Works very similar to prompt_menu except it takes in the message and a list of reactions instead of the specific menu_items."""

	for r in list_of_emojis:
		bot.loop.create_task(msg.add_reaction(r))

	def check(payload):
		log.debug(f"checking payload {payload}")
		return payload.message_id == msg.id and payload.user_id == user.id and str(
			payload.emoji
		) in list_of_emojis

	try:
		log.debug("waiting for user's reaction")
		# HACK: reaction_add doesn't work in DMs
		payload = await bot.wait_for("raw_reaction_add", check=check)
	except asyncio.TimeoutError as e:
		log.error("timed out")
		raise e

	reactionId = list_of_emojis.index(str(payload.emoji))

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

	title = battlecontext.pokemon.Name
	description = f"{battlecontext.pokemon.CurrentHP} HP {taggify(type_to_string(battlecontext.pokemon.Type))} {taggify(status_to_string(battlecontext.pokemon.StatusEffects))}"
	content = "Select a move"

	menu_items = []
	for i, move in enumerate(battlecontext.pokemon.Moves):
		menu_items.append(
			(
				f"{move['Name']}",
				f"{taggify(type_to_string(move['Type']))} {move['CurrentPP']}/{move['MaxPP']}"
			)
		)

	moveId = await prompt_menu(
		bot, user, content, title, description, menu_items, use_channel
	)

	target = battlecontext.opponents[0]
	return FightTurn(party=target.party, slot=target.slot, move=moveId)


def status_to_string(status: int) -> set[str]:
	"""Get the human-readbale form of a Pokemon's Status Condition.

	:param status: pokemon battle status as defined in pokemonbattlelib
	:type status: int
	:raises ValueError: raised if `status` is not of the proper format
	:return: a set of status name strings
	:rtype: set
	"""

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

	elements = [
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
	return set(
		[flag for (index, flag) in enumerate(elements) if (elemental_type & 1 << index)]
	)


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


def prettify_all_transactions(transactions: list[Transaction]) -> list[str]:
	"""Prettify all transactions, and concatenate/truncate them such that they fit inside the description of a :class:`discord.Embed`.

	:param transactions: The list of transactions to prettify.
	"""
	transactions_text: list[str] = []
	current = ""
	char_limit = 2048
	while len(transactions) > 0:
		t = transactions.pop(0)
		# log.debug(f"Transaction: {repr(t)}")
		pretty = t.pretty()
		if len(current) + len(pretty) > char_limit:
			if len(current) > 0:
				transactions_text += [current]
			if len(pretty) > char_limit:
				log.warning(
					f"Transaction's pretty text is too long! Truncating to {char_limit} chars."
				)
				transactions_text += [pretty[:char_limit]]
				continue
			current = ""
		current += pretty + "\n"
	if len(current) > 0:
		transactions_text += [current]
	return transactions_text
