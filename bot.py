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
import coloredlogs
from userprofile import UserProfile, load_profile
import Levenshtein

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=log)

lock = asyncio.Lock()


class DiscordBrock(commands.Bot):
	"""A class that allows the bot to listen for other bots.

	:: note
		Required because of https://github.com/Rapptz/discord.py/issues/2238
	"""

	async def on_message(self, message: Message): # noqa: D102
		ctx = await self.get_context(message)
		if ctx.valid:
			await self.invoke(ctx)


bot = DiscordBrock(command_prefix='p!')


@bot.command()
async def ping(ctx: commands.Context): # noqa: D103
	await ctx.send('pong')
	log.warning('log message')


@bot.command()
async def challenge(ctx: commands.Context, opponent: str): # noqa: D103
	base_msg = f"<@!{ctx.author.id}> challenging {opponent}"
	msg: Message = await ctx.send(base_msg)
	await msg.edit(content=f"{base_msg} (Populating battle...)")
	pkmn = [await battleapi.generate_pokemon() for _ in range(2)]

	teams = util.build_teams_single([pkmn[0]], [pkmn[1]])
	battle = coordinator.Battle(teams=teams, original_channel=ctx.channel)
	battle.add_user(ctx.author)
	if opponent.startswith("<@") and opponent.endswith(">"):
		user = ctx.message.mentions[0]
		battle.add_user(user)
	else:
		battle.add_bot(opponent)
	coordinator.battles += [battle]
	await battle.start()
	await msg.edit(content=f"{base_msg} (Started)")


def get_token():
	"""Read the bot's token from disk."""
	with open("token", "r") as f:
		return "".join(f.readlines()).strip()


@bot.command()
async def minigame(ctx: commands.Context): # noqa: D103
	"""Minigame to allow users to acquire Pokemon."""
	await lock.acquire()

	pokemon = await battleapi.generate_pokemon()
	name = pokemon.Name

	embed = discord.Embed(
		title="Who's That Pokemon?",
		description="Can you guess the name of the Pokemon shown below?",
		color=0x00ff00
	)

	file = discord.File(pokemon.get_silhouette(), filename="whosthatpokemon.png")
	embed.set_image(url="attachment://whosthatpokemon.png")
	# embed.add_field(name="Commands", value="Please format all guesses like `guess pokemonName`, and if you need help type `guess hint`")
	embed.add_field(name="Guess", value="`guess pokemonName`")
	embed.add_field(name="Help", value="`guess hint`")
	await ctx.send(file=file, embed=embed)

	def check(m):
		return m.id != bot.user.id and m.channel == ctx.channel and m.content.startswith(
			"guess"
		)

	message = await bot.wait_for("message", check=check)
	guess = message.content.split()[-1]

	while guess.lower() != name.lower():
		if guess.lower() == "hint":
			await ctx.send(
				f"The name of this **{util.type_to_string(pokemon.Type).pop()} type** pokemon starts with the letter **{name[0]}**"
			)
		elif Levenshtein.distance(guess.lower(), name.lower()) < 3:
			await ctx.send(
				f"{message.author.mention} that guess was close, but not quite right"
			)
		else:
			await ctx.send("That's incorrect, please guess again")
		message = await bot.wait_for("message", check=check)
		guess = message.content.split()[-1]

	file = discord.File(pokemon.get_silhouette(), filename="whosthatpokemon.png")
	embed.set_image(url="attachment://whosthatpokemon.png")
	embed.add_field(name="Guess", value="`guess pokemonName`")
	embed.add_field(name="Help", value="`guess hint`")
	await ctx.send(file=file, embed=embed)

	await ctx.send(
		f"Nice one, {message.author.mention}, that's correct! Adding {name} to your inventory"
	)
	await ctx.send(
		file=discord.File(f"/code/images/{pokemon.NatDex}.png", filename=f"{name}.png")
	)

	await pokemon.save()
	profile = UserProfile()
	profile.user_id = message.author.id
	profile.add_pokemon(pokemon)
	await profile.save()
	lock.release()


if __name__ == "__main__":
	coordinator.set_bot(bot)
	# reference: https://pgjones.gitlab.io/quart/how_to_guides/event_loop.html
	bot.loop.create_task(serve.app.run_task(host="0.0.0.0", use_reloader=False))
	bot.run(get_token())
