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
import userprofile

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=log)


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
	#log.warning('log message')


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


@bot.command()
async def begin(ctx: commands.Context): # noqa: D103
	if (profile := await userprofile.load_profile(ctx.author.id)) != None:
		assert isinstance(profile, userprofile.UserProfile)
		await ctx.send(f"You've already started a profile!", embed=profile.get_embed())
		return
	log.debug(f"{ctx.author} creating new profile.")
	profile = userprofile.UserProfile()
	profile.user_id = ctx.author.id
	starter_dexnums = [1, 4, 7, 25, 152, 155, 158, 252, 255, 258, 387, 390, 393]
	starters = [
		await battleapi.generate_pokemon(natdex=natdex, level=5)
		for natdex in starter_dexnums
	]
	items = [pkmn.Name for pkmn in starters]
	selection = await util.prompt_menu(
		bot,
		ctx.author,
		content=f"<@!{ctx.author.id}>",
		title="Choose your starter",
		description="Don't worry, you'll be able to get more later!",
		items=items,
		use_channel=ctx.channel
	)
	selected_pokemon = starters[selection]
	log.debug(f"{ctx.author} selected {selected_pokemon.Name}")
	await selected_pokemon.save()
	profile.add_pokemon(selected_pokemon)
	await profile.save()
	log.info(f"New profile: {ctx.author}")
	await ctx.send("Profile created! `p!help` for more commands.")


@bot.command(help='Add name to display specific Pokemon')
async def show(ctx: commands.Context, single: Optional[str]): # noqa: D103
	discord_id = ctx.author.id
	base_msg = f"<@!{discord_id}> Here are all of your current Pokemon"
	msg: Message = await ctx.send(base_msg)
	#loads user class based upon their discord_id
	user = await userprofile.load_profile(discord_id)
	if single:
		async for pokemon in user.pokemon_iter():
			if pokemon.Name == single:
				Message = await ctx.send(
					f"{pokemon.Name}: {pokemon.CurrentHP} HP {util.taggify(util.type_to_string(pokemon.Type))}"
				)
				Message = await ctx.send(
					f"Level: {pokemon.Level}\nExp: {pokemon.TotalExperience}"
				)
	else:
		async for pokemon in user.pokemon_iter():
			Message = await ctx.send(
				f"{pokemon.Name}: {pokemon.CurrentHP} HP {util.taggify(util.type_to_string(pokemon.Type))}"
			)


def get_token():
	"""Read the bot's token from disk."""
	with open("token", "r") as f:
		return "".join(f.readlines()).strip()


if __name__ == "__main__":
	coordinator.set_bot(bot)
	# reference: https://pgjones.gitlab.io/quart/how_to_guides/event_loop.html
	bot.loop.create_task(serve.app.run_task(host="0.0.0.0", use_reloader=False))
	bot.run(get_token())
