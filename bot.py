import asyncio
import json
import aiohttp
import logging
import discord
from discord.ext import commands
from discord.message import Message
import serve, coordinator
from pkmntypes import *
import util
import battleapi

bot = commands.Bot(command_prefix='p!')

@bot.command()
async def ping(ctx: commands.Context):
	await ctx.send('pong')

@bot.command()
async def challenge(ctx: commands.Context, opponent: str):
	await ctx.send(f"<@!{ctx.author.id}> challenging {opponent}")
	msg = await ctx.send("Populating battle...")
	pkmn = [await battleapi.generate_pokemon() for _ in range(2)]

	teams = util.build_teams_single([pkmn[0]], [pkmn[1]])
	battle = coordinator.Battle(teams=teams, original_channel=ctx.channel)
	battle.add_user(ctx.author)
	if opponent.startswith("<@!") and opponent.endswith(">"):
		user = ctx.message.mensions[0]
		battle.add_user(user)
	else:
		battle.add_bot(opponent)
	coordinator.battles += [battle]
	await battle.start()
	await msg.edit(content="Battle started.")

def get_token():
	with open("token", "r") as f:
		return "".join(f.readlines()).strip()

if __name__ == "__main__":
	coordinator.set_bot(bot)
	# reference: https://pgjones.gitlab.io/quart/how_to_guides/event_loop.html
	bot.loop.create_task(serve.app.run_task(host="0.0.0.0", use_reloader=False))
	bot.run(get_token())
