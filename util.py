import discord
import logging, asyncio
from discord.ext import commands
from discord.message import Message
from turns import *

RESPONSE_REACTIONS = ["🇦", "🇧", "🇨", "🇩"]

async def prompt_for_turn(bot: commands.Bot, user: discord.User, battlecontext) -> Turn:
	# TODO: create an actual class for battlecontext instead of just parsing the json into a dict like a monkey
	# TODO: prompt user for what type of turn

	if not user.dm_channel:
		await user.create_dm()
	embed = discord.Embed(title=battlecontext["Pokemon"]["Name"])
	for move in battlecontext["Pokemon"]["Moves"]:
		embed.add_field(name=move['Name'], value=f"{move['Type']} {move['CurrentPP']} {move['MaxPP']}")
	msg: Message = await user.dm_channel.send(content="Select a move", embed=embed)
	for i in RESPONSE_REACTIONS:
		await msg.add_reaction(i)
	def check(payload):
		logging.debug(f"checking payload {payload}")
		return payload.message_id == msg.id and payload.user_id == user.id and str(payload.emoji) in RESPONSE_REACTIONS
	try:
		logging.debug("waiting for user's reaction")
		# HACK: reaction_add doesn't work in DMs
		payload = await bot.wait_for("raw_reaction_add", check=check)
	except asyncio.TimeoutError:
		await user.dm_channel.send("timed out")
		return

	moveId = RESPONSE_REACTIONS.index(str(payload.emoji))

	# TODO: prompt for which pokemon to target in double battles
	target = battlecontext["Opponents"][0]
	return FightTurn(party=target["Party"], slot=target["Slot"], move=moveId)

def status_to_string(status: int) -> set:
	"""Returns the human-readbale form of a Pokemon's Status Condition

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
		volatile = [flag for (index, flag) in enumerate(volatile) if (bitmask & 2 ** index)]
		return set(nonvolatile + volatile)
	except:
		raise ValueError("invalid value for status")
