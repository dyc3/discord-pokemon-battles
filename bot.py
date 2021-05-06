import asyncio
import io
import json
import aiohttp
import logging, time
import discord
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType
from discord.message import Message
import serve, coordinator
from pkmntypes import *
import util
import battleapi
import coloredlogs
import userprofile
import Levenshtein
from typing import Callable, Union, Any
import config

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=log)


class DiscordBrock(commands.Bot):
	"""A class that allows the bot to listen for other bots.

	:: note
		Required because of https://github.com/Rapptz/discord.py/issues/2238
	"""

	async def on_message(self, message: Message): # noqa: D102
		ctx = await self.get_context(message)
		userprofile.add_user_to_cache(ctx.author)
		map(userprofile.add_user_to_cache, ctx.message.mentions)
		if ctx.valid:
			await self.invoke(ctx)


bot = DiscordBrock(command_prefix='p!')


def dev_command(*args, **kwargs):
	"""Disable a discord command in production. Must **not** be used with `@bot.command()` decorator. Takes the same arguments as `@bot.command()`.

	Example:
	```
	@dev_command()
	async def dev_only(ctx: commands.Context):
		pass
	```
	"""
	if config.BROCK_ENVIRONMENT == "dev-test":

		def decorator(func):
			log.warning(f"adding dev command to bot: {func.__name__}")
			return bot.command(*args, **kwargs)(func)

		return decorator
	else:

		def decorator(func):
			log.debug(f"skip adding dev command to bot: {func.__name__}")
			return func

		return decorator


@dev_command()
async def ping(ctx: commands.Context): # noqa: D103
	await ctx.send('pong')


@bot.command(
	help="""Start a battle with another user or a battle bot.

	See available battle bots with `p!battlebots`.
	"""
)
async def challenge(
	ctx: commands.Context,
	opponent: str,
	level: int = 30,
	party_size: int = 1
): # noqa: D103
	if level < 1 or level > 100:
		raise commands.BadArgument(
			f'Level must be between 1 and 100 (inclusive), but got {level}'
		)
	if party_size < 1 or party_size > 6:
		raise commands.BadArgument(
			f'Party size must be between 1 and 6 (inclusive), but got {party_size}'
		)
	log.debug(f"Setting up battle: {ctx.author} challenging {opponent}")
	start_time = time.time()
	pkmn = [await battleapi.generate_pokemon(level=level) for _ in range(party_size * 2)]

	teams = util.build_teams_single(pkmn[:party_size], pkmn[party_size:])
	battle = coordinator.Battle(teams=teams, original_channel=ctx.channel)
	battle.add_user(ctx.author)
	if opponent.startswith("<@") and opponent.endswith(">"):
		user = ctx.message.mentions[0]
		if user.bot:
			await ctx.send(content="You can't challege a discord bot.")
			return
		battle.add_user(user)
	else:
		if opponent == "bot":
			opponent = "simple"
		import battle_ai
		if opponent not in battle_ai.strategies:
			raise commands.BadArgument(
				f"{opponent} is not a valid battle bot. See `p!battlebots`."
			)
		battle.add_bot(opponent)
	async with coordinator.battles_lock:
		coordinator.battles += [battle]
	duration = time.time() - start_time
	log.info(f"Battle setup took {duration} seconds. Starting battle...")
	await battle.start()


@bot.command(
	help="""Simulate a battle between 2 bots.

	Useful for simulating heavy bot usage.
	See available battle bots with `p!battlebots`.
	"""
)
async def simulate(
	ctx: commands.Context, bot1, bot2, level=100, party_size=6
): # noqa: D103
	if bot1 == "bot":
		bot1 = "simple"
	if bot2 == "bot":
		bot2 = "simple"
	import battle_ai
	if bot1 not in battle_ai.strategies:
		raise commands.BadArgument(
			f"{bot1} is not a valid battle bot. See `p!battlebots`."
		)
	if bot2 not in battle_ai.strategies:
		raise commands.BadArgument(
			f"{bot2} is not a valid battle bot. See `p!battlebots`."
		)
	if level < 1 or level > 100:
		raise commands.BadArgument(
			f'Level must be between 1 and 100 (inclusive), but got {level}'
		)
	if party_size < 1 or party_size > 6:
		raise commands.BadArgument(
			f'Party size must be between 1 and 6 (inclusive), but got {party_size}'
		)
	log.debug(f"Setting up battle: {bot1} challenging {bot2}")
	start_time = time.time()
	pkmn = [await battleapi.generate_pokemon(level=level) for _ in range(party_size * 2)]

	teams = util.build_teams_single(pkmn[:party_size], pkmn[party_size:])
	battle = coordinator.Battle(teams=teams, original_channel=ctx.channel)
	battle.add_bot(bot1)
	battle.add_bot(bot2)
	async with coordinator.battles_lock:
		coordinator.battles += [battle]
	duration = time.time() - start_time
	log.info(f"Battle setup took {duration} seconds. Starting battle...")
	await battle.start()


@bot.command(help='Create a profile and choose your starter Pokemon.')
@commands.max_concurrency(1, per=BucketType.user, wait=False)
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
	try:
		selection = await asyncio.wait_for(
			util.prompt_menu(
				bot,
				ctx.author,
				content=f"<@!{ctx.author.id}>",
				title="Choose your starter",
				description="Don't worry, you'll be able to get more later!",
				items=items,
				use_channel=ctx.channel
			),
			timeout=60
		)
	except asyncio.TimeoutError:
		await ctx.send(
			"`begin`: You took too long to respond. You'll have to run the command again."
		)
		return
	selected_pokemon = starters[selection]
	log.debug(f"{ctx.author} selected {selected_pokemon.Name}")
	await selected_pokemon.save()
	profile.add_pokemon(selected_pokemon)
	await profile.save()
	log.info(f"New profile: {ctx.author}")
	await ctx.send("Profile created! `p!help` for more commands.")


@dev_command()
async def test_prompt_message(ctx: commands.Context):
	"""Tests the prompt_message function."""
	msg = await ctx.send("Choose an option")
	emojis = ["🇦", "🇧", "🇨", "🇩"]
	result = await util.prompt_message(bot, ctx.author, msg, emojis)
	await ctx.send(f"got: {result}")


@bot.command(help='List your current pokemon.')
async def show(ctx: commands.Context, single: Optional[str]): # noqa: D103
	texts = [f"{ctx.author.mention} Here are all of your current Pokemon"]
	if (user := await userprofile.load_profile(ctx.author.id)):
		async for pokemon in user.pokemon_iter():
			if single and pokemon.Name == single or not single:
				texts += [
					f"{pokemon.Name}: {util.safe_display_types(pokemon.Type)} Lv{pokemon.Level} Moves: {', '.join(map(lambda m: m.name_and_type, pokemon.Moves))}"
				]
	else:
		await ctx.send(
			"Couldn't find a profile! Make sure you create a profile by typing `p!begin`"
		)
		return

	await ctx.send("\n".join(texts))


@dev_command()
async def callMinigame(ctx: commands.Context, natdex: str = ""):
	"""Call the minigame function, optionally with a pokemon specified by natdex number.

	This command is for development and testing purposes only.
	"""
	pokemon = await battleapi.generate_pokemon(natdex=int(natdex) if natdex else None)
	await minigame(ctx.channel, pokemon=pokemon)


async def minigame(
	channel: Union[discord.abc.Messageable], pokemon: Pokemon = None
): # noqa: D103
	"""Minigame to allow users to acquire Pokemon.

	By default presents users with a random pokemon, but optionally uses a specified pokemon.
	"""

	if pokemon is None:
		pokemon = await battleapi.generate_pokemon()

	name = pokemon.Name

	embed = discord.Embed(
		title="Who's That Pokemon?",
		description="Can you guess the name of the Pokemon shown below?",
		color=0x00ff00
	)

	file = discord.File(pokemon.get_silhouette(), filename="whosthatpokemon.png")
	embed.set_image(url="attachment://whosthatpokemon.png")
	embed.add_field(name="Guess", value="`guess pokemonName`")
	embed.add_field(name="Help", value="`guess hint`")
	await channel.send(file=file, embed=embed)

	def check(m):
		return m.id != bot.user.id and m.channel == channel and m.content.startswith(
			"guess"
		)

	async def run():
		while True:
			message: Message = await bot.wait_for("message", check=check)
			guess = message.content.split()[-1]
			profile = await userprofile.load_profile(message.author.id)

			if profile is None:
				await channel.send(
					f"{message.author.mention} you need to run `p!begin` before you can play the game"
				)
			elif guess.lower() == "hint":
				await channel.send(
					f"The name of this **{util.type_to_string(pokemon.Type).pop()} type** pokemon starts with the letter **{name[0]}**"
				)
			elif guess.lower() == name.lower(): # a correct guess ends the minigame
				return message, profile
			elif Levenshtein.distance(guess.lower(), name.lower()) < 3:
				await channel.send(
					f"{message.author.mention} that guess was close, but not quite right"
				)
			else:
				await channel.send("That's incorrect, please guess again")

	try:
		message, profile = await asyncio.wait_for(run(), timeout=60)
	except asyncio.TimeoutError:
		await channel.send(
			f"Aw, nobody guessed right, and **{pokemon.name_and_type}** ran away..."
		)
		return

	embed = discord.Embed(
		title="Correct!",
		description=
		f"Nice one, {message.author.mention}, that's right! Adding {name} to your inventory",
		color=0x00ff00
	)

	file = discord.File(f"./images/{pokemon.NatDex}.png", filename=f"{name}.png")
	embed.set_image(url=f"attachment://{name}.png")
	await channel.send(file=file, embed=embed)
	await pokemon.save()
	profile.add_pokemon(pokemon)
	await profile.save()


@dev_command(help="Force the storage module to point to the test database.")
async def use_test_db(ctx: commands.Context):
	"""Force the storage module to point to the test database. Requires a restart to revert."""
	from motor.motor_asyncio import AsyncIOMotorClient
	import storage
	client = AsyncIOMotorClient('mongodb://db/brock_test')
	storage._set_client(client)
	log.warning(
		f"Now using database: {storage.db.name}. Restart required to revert this change."
	)
	await ctx.send(f"Using database: {storage.db.name}")


@bot.command(
	help="Add the bot's custom emoji to this server. This is probably not necessary."
)
@commands.bot_has_guild_permissions(manage_emojis=True)
async def generate_emoji(ctx: commands.Context): # noqa: D103
	log.info("generating and adding emoji to server")
	import visualize
	guild: discord.Guild = ctx.guild
	added_emoji = []
	for e in TYPE_ELEMENTS:
		ename = util.type_emoji_name(e)
		if discord.utils.get(bot.emojis, name=ename) != None:
			log.debug(f"Already have access to {ename}, skipping...")
			continue
		with io.BytesIO() as data:
			im = visualize.get_element_type_img(e)
			im.resize(visualize.scale(im.size, 4), Image.NEAREST).save(data, 'PNG')
			data.seek(0)
			log.debug(f"creating emoji {ename}")
			emoji = await guild.create_custom_emoji(
				name=ename, image=data.getvalue(), reason="Added by Brock"
			)
		util.cache_emoji(emoji)
		added_emoji += [emoji]
	for cond in StatusCondition.NonVolatile:
		if cond in [
			StatusCondition.NonVolatile.none, StatusCondition.NonVolatile.badly_poison
		]:
			continue
		status = StatusCondition(non_volatile=cond)
		ename = f"status{cond}"
		if discord.utils.get(bot.emojis, name=ename) != None:
			log.debug(f"Already have access to {ename}, skipping...")
			continue
		with io.BytesIO() as data:
			im = visualize.get_status_condition_img(status)
			im.resize(visualize.scale(im.size, 6), Image.NEAREST).save(data, 'PNG')
			data.seek(0)
			log.debug(f"creating emoji {ename}")
			emoji = await guild.create_custom_emoji(
				name=ename, image=data.getvalue(), reason="Added by Brock"
			)
		util.cache_emoji(emoji)
		added_emoji += [emoji]

	await ctx.send(
		f"Added custom emoji to this server: {' '.join(map(str, added_emoji))}"
	)


@bot.event
async def on_ready(): # noqa: D103
	cache_all_emojis()
	await bot.change_presence(activity=discord.Game(name="p!help for commands"))


def cache_all_emojis():
	"""Cache all emojis that the bot currently has available to it."""
	log.debug("cache_all_emojis()")
	for emoji in bot.emojis:
		util.cache_emoji(emoji)


@dev_command()
async def ensure_profile(ctx: commands.Context):
	"""Ensure that there is a profile created for the user that calls this command."""
	profile = await userprofile.load_profile(ctx.author.id)
	if not profile:
		profile = userprofile.UserProfile()
		pkmn = await battleapi.generate_pokemon()
		await pkmn.save()
		profile.add_pokemon(pkmn)
	profile.user_id = ctx.author.id
	await profile.save()
	await ctx.send("OK")


@bot.command(help="Start the minigame in this channel.")
@commands.guild_only()
@commands.max_concurrency(1, per=BucketType.channel, wait=False)
async def encounter(ctx: commands.Context): # noqa: D103
	if await userprofile.load_profile(ctx.author.id) == None:
		await ctx.send("You need to have a profile. Run `p!begin`.")
		return
	await minigame(ctx.channel)


@bot.command(help="List all available battle bots")
async def battlebots(ctx: commands.Context): # noqa: D103
	import battle_ai
	await ctx.send(
		f"All available battle bots: {', '.join(map(lambda x: f'`{x}`', battle_ai.strategies.keys()))}"
	)


if __name__ == "__main__":
	coordinator.set_bot(bot)
	# reference: https://pgjones.gitlab.io/quart/how_to_guides/event_loop.html
	bot.loop.create_task(serve.app.run_task(host="0.0.0.0", use_reloader=False))
	bot.load_extension("cogs.error_handler_fallback")
	import storage
	bot.loop.create_task(storage.set_validators())

	bot.run(config.BOT_TOKEN)
