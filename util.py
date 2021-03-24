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

def status_to_string(status):
	"""Returns the human-readbale form of a Pokemon's Status Condition

	:param status: pokemon battle status as defined in pokemonbattlelib
	:type status: int

	:return: the name of the status
	:rtype: string
	"""
    statuses = {
        0: "None",
		# non volatile:
        1: "Burn",
        2: "Freeze",
        3: "Paralyze",
        4: "Poison",
        5: "BadlyPoison",
        6: "Sleep",
        # volatile:
        8: "Bound",
        16: "CantEscape",
        32: "Confusion",
        64: "Cursed",
        12: "Embargo",
        25: "Flinch",
        51: "HealBlock",
        104: "Identified",
        208: "Infatuation",
        406: "LeechSeed",
        812: "Nightmare",
        1684: "PerishSong",
        32768: "Taunt",
        65536: "Torment",
    }
    return statuses[int(status)]