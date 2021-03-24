import discord
import logging, asyncio
from discord.ext import commands
from discord.message import Message
from turns import *
from typing import Union
from pkmntypes import *

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

def build_teams_single(*parties: Union[list[Party], list[list[Pokemon]]]) -> list[Team]:
	"""
	Takes 2 parties of pokemon, creates a list of teams suitable to create a single battle.

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
