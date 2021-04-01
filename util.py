import discord
import logging, asyncio
from discord.ext import commands
from discord.message import Message
from turns import *
from typing import Iterable, Union
from pkmntypes import *

RESPONSE_REACTIONS = ["🇦", "🇧", "🇨", "🇩"]


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

	if use_channel:
		channel = use_channel
	else:
		if not user.dm_channel:
			await user.create_dm()
		channel = user.dm_channel
	embed = discord.Embed(
		title=battlecontext.pokemon.Name,
		description=
		f"{battlecontext.pokemon.CurrentHP} HP {taggify(type_to_string(battlecontext.pokemon.Type))} {taggify(status_to_string(battlecontext.pokemon.StatusEffects))}"
	)
	for i, move in enumerate(battlecontext.pokemon.Moves):
		embed.add_field(
			name=f"{RESPONSE_REACTIONS[i]}: {move['Name']}",
			value=
			f"{taggify(type_to_string(move['Type']))} {move['CurrentPP']}/{move['MaxPP']}",
			inline=False
		)
	msg: Message = await channel.send(content="Select a move", embed=embed)
	for r in RESPONSE_REACTIONS:
		await msg.add_reaction(r)

	def check(payload):
		logging.debug(f"checking payload {payload}")
		return payload.message_id == msg.id and payload.user_id == user.id and str(
			payload.emoji
		) in RESPONSE_REACTIONS

	try:
		logging.debug("waiting for user's reaction")
		# HACK: reaction_add doesn't work in DMs
		payload = await bot.wait_for("raw_reaction_add", check=check)
	except asyncio.TimeoutError as e:
		await channel.send("timed out")
		raise e

	moveId = RESPONSE_REACTIONS.index(str(payload.emoji))

	# TODO: prompt for which pokemon to target in double battles
	target = battlecontext.opponents[0]
	return FightTurn(party=target.party, slot=target.slot, move=moveId)


def status_to_string(status: int) -> set:
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
