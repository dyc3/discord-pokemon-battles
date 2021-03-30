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


class PkmnBot(commands.Bot):
	"""
	A class that allows the bot to listen for other bots.

	:: note
		Required because of https://github.com/Rapptz/discord.py/issues/2238
	"""

	async def on_message(self, message): # noqa: D103
		ctx = await self.get_context(message)
		if ctx.valid:
			await self.invoke(ctx)


bot = PkmnBot(command_prefix='p!')


@bot.command()
async def ping(ctx: commands.Context): # noqa: D103
	await ctx.send('pong')


@bot.command()
async def challenge(ctx: commands.Context, opponent: str): # noqa: D103
	base_msg = f"<@!{ctx.author.id}> challenging {opponent}"
	msg: Message = await ctx.send(base_msg)
	await msg.edit(content=f"{base_msg} (Populating battle...)")
	pkmn = [await battleapi.generate_pokemon() for _ in range(2)]

	# FIXME: temporarily ignored type check
	teams = util.build_teams_single([pkmn[0]], [pkmn[1]]) # type: ignore
	battle = coordinator.Battle(teams=teams, original_channel=ctx.channel)
	battle.add_user(ctx.author)
	if opponent.startswith("<@!") and opponent.endswith(">"):
		user = ctx.message.mensions[0]
		battle.add_user(user)
	else:
		battle.add_bot(opponent)
	coordinator.battles += [battle]
	await battle.start()
	await msg.edit(content=f"{base_msg} (Started)")


def get_token():
	with open("token", "r") as f:
		return "".join(f.readlines()).strip()


if __name__ == "__main__":
	coordinator.set_bot(bot)
	# reference: https://pgjones.gitlab.io/quart/how_to_guides/event_loop.html
	bot.loop.create_task(serve.app.run_task(host="0.0.0.0", use_reloader=False))
	bot.run(get_token())
