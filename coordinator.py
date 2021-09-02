from typing import Callable, Union, Any, Optional
import io
import asyncio
import aiohttp
import functools
import discord
from discord import embeds
from turns import *
import util
import battleapi
from pkmntypes import *
from discord.message import Message
from visualize import visualize_battle
import battle_ai
import traceback
import logging, coloredlogs

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=log)


def set_bot(b):
	"""Set the bot that the coordinator should use."""

	global bot
	bot = b


class Agent():
	"""An handles grabbing input from the user or AI and makes it available for the :class:`Battle`."""

	def __init__(self, user=None, bot=None):
		self.user: discord.User = user
		self.bot: str = bot
		if bot == "bot":
			self.bot = "simple"

	async def send_visualization(
		self, ctx: BattleContext, channel: discord.TextChannel = None
	) -> None:
		"""Send battlefield visualization to the agent."""
		if self.user != None:
			if not self.user.bot:
				if not self.user.dm_channel:
					await self.user.create_dm()
				channel = self.user.dm_channel
			if channel:
				with channel.typing():
					with io.BytesIO() as data:
						visualize_battle(ctx).save(data, 'PNG')
						data.seek(0)
						await channel.send(file=discord.File(data, filename="battle.png"))

	async def get_turn(
		self, context: BattleContext, original_channel: discord.TextChannel
	) -> Turn:
		"""Get a turn from the Agent."""

		log.debug(f"getting turn from {self}")
		if self.bot != None:
			assert self.bot in battle_ai.strategies, f"Invalid battle strategy for bot: {self.bot}"
			return battle_ai.strategies[self.bot](context)
		if self.user != None:
			return await util.prompt_for_turn(
				bot, # type: ignore
				self.user,
				context,
				use_channel=original_channel if self.user.bot else None
			)
		raise Exception("Failed to get turn from agent")

	def __str__(self):
		if self.bot != None:
			return f"Agent<Bot: {self.bot}>"
		if self.user != None:
			return f"Agent<User: {self.user.name}>"
		return f"Agent<invalid>"

	@property
	def name(self) -> str:
		"""Get the name of this agent."""
		if self.bot != None:
			return self.bot
		return str(self.user.name)

	@property
	def mention(self) -> str:
		"""Get a string that mentions this agent on discord."""
		if self.bot != None:
			return self.bot
		return str(self.user.mention)


class Battle():
	"""A Pokemon battle. Gathers user input and manages the simulation via the battle api."""

	def __init__(self, **kwargs):
		self.bid: int = None
		self.active_pokemon: int = None
		self.agents: list[Agent] = []
		self.transactions: list[Transaction] = []
		self.original_channel: discord.TextChannel = kwargs.pop("original_channel", None)
		self.teams: list[Team] = kwargs.pop("teams")

	def add_user(self, user: discord.User):
		"""Add a user Agent to the battle."""
		assert user != None
		assert isinstance(user, discord.User) or isinstance(
			user, discord.Member
		), f"user should not be {type(user)}"
		self.agents.append(Agent(user=user))

	def add_bot(self, botname: str):
		"""Add a bot Agent to the battle."""
		self.agents.append(Agent(bot=botname))

	@property
	def is_just_bots(self):
		"""Get whether or not the battle only consists of bot agents."""
		return all([a.bot != None and len(a.bot) > 0 for a in self.agents])

	async def start(self):
		"""Create the battle on the battle API, making the battle ready to simulate, and starts a task asynchronously to simulate the battle."""
		args = await battleapi.create_battle(self.teams)
		self.bid = args["bid"]
		self.active_pokemon = args["active_pokemon"]
		bot.loop.create_task(self.simulate())

	async def queue_turns(self):
		"""Request and queue turns from all agents in the battle."""
		log.debug(f"asking {len(self.agents)} agents")

		async def _do(i: int, agent: Agent):
			context = await battleapi.get_battle_context(self.bid, i)
			await agent.send_visualization(context)
			turn = await agent.get_turn(context, self.original_channel)
			log.debug(f"posting turn {turn} from {agent}")
			await battleapi.submit_turn(self.bid, i, turn)

		await asyncio.gather(*[_do(i, agent) for i, agent in enumerate(self.agents)])

	async def simulate(self):
		"""Simulate the entire battle. Asynchronously blocks until the battle is completed."""
		try:
			while True:
				log.debug("visualizing")
				spectator_embed = discord.Embed(
					title=f"{self.agents[0].name} vs. {self.agents[1].name}",
					description="Waiting for turns..."
				)
				spectator_content = f"{self.agents[0].mention} vs. {self.agents[1].mention}"

				ctx = await battleapi.get_battle_context(self.bid, 0)
				if not self.is_just_bots:
					with self.original_channel.typing():
						with io.BytesIO() as data:
							visualize_battle(ctx).save(data, 'PNG')
							data.seek(0)
							spectator_embed.set_image(url="attachment://battle.png")
							spectator_msg: discord.Message = await self.original_channel.send(
								spectator_content,
								embed=spectator_embed,
								file=discord.File(data, filename="battle.png")
							)
				log.debug("asking agents for turns")
				await self.queue_turns()
				log.debug("simulating round")
				results = await battleapi.simulate(self.bid)
				self.transactions += results.transactions
				# embed descriptions can only be 2048 characters long.
				char_limit = 2048
				transactions_text = util.prettify_all_transactions(results.transactions)

				if len(transactions_text) == 1:
					spectator_embed.description = transactions_text[0]
				else:
					# if the text doesn't fit on one embed, just put all the transactions into new messages
					with self.original_channel.typing():
						for text in transactions_text:
							if len(text) > char_limit:
								log.warning(
									f"Embed's text is too long! Truncating to {char_limit} chars."
								)
								text = text[:char_limit]
							await self.original_channel.send(
								embed=discord.
								Embed(title=spectator_embed.title, description=text)
							)
				for agent in self.agents:
					if agent.user:
						if len(transactions_text) == 0:
							transactions_text = "[No transactions]"
							await agent.user.dm_channel.send(
								embed=discord.Embed(description="[No transactions]")
							)
							continue
						with agent.user.dm_channel.typing():
							for text in transactions_text:
								if len(text) > char_limit:
									log.warning(
										f"Embed's text is too long! Truncating to {char_limit} chars."
									)
									text = text[:char_limit]
								assert len(
									text
								) > 0, f"found empty message in transaction_text, which should not happen {transactions_text}"
								await agent.user.dm_channel.send(
									embed=discord.Embed(description=text)
								)
				if not self.is_just_bots:
					await spectator_msg.edit(embed=spectator_embed)
				else:
					with io.BytesIO() as data:
						visualize_battle(ctx).save(data, 'PNG')
						data.seek(0)
						spectator_embed.set_image(url="attachment://battle.png")
						spectator_msg: discord.Message = await self.original_channel.send(
							spectator_content,
							embed=spectator_embed,
							file=discord.File(data, filename="battle.png")
						)
				if results.ended:
					break
				if self.is_just_bots:
					await asyncio.sleep(2)
			log.info(f"Battle between {self.agents} concluded")
			results = await battleapi.get_results(self.bid)
			if self.original_channel:
				embed = self.__create_battle_summary_msg(results)
				battle_sum_msg: Message = await self.original_channel.send(embed=embed)
				if not isinstance(self.original_channel, discord.DMChannel):
					link = util.get_link(battle_sum_msg)
					for agent in self.agents:
						if agent.user:
							embed.description = f"[Click here to go back]({link})"
							await agent.user.dm_channel.send(embed=embed)
			await self.apply_post_battle_updates(results)
		except Exception as e:
			log.critical(
				f"Unhandled error occured during battlle: {e}\n{''.join(traceback.format_exception(type(e), e, e.__traceback__))}"
			)
			for agent in self.agents:
				if agent.user:
					try:
						await agent.user.dm_channel.send(
							"Whoops, something bad happened, so the battle has been discarded."
						)
					except discord.HTTPException:
						pass
		finally:
			await self.__cleanup()

	async def apply_post_battle_updates(self, results: battleapi.BattleResults):
		"""Apply post battle state updates to pokemon, and save them to storage."""

		log.debug(f"Applying new stats to pokemon")
		playerparties = functools.reduce(
			lambda a, b: a + b, [team.parties for team in self.teams]
		)
		try:
			for party, resultParty in zip(playerparties, results.parties):
				assert isinstance(party, Party)
				assert isinstance(resultParty, Party)
				for pkmn, resultPkmn in zip(party.pokemon, resultParty.pokemon):
					assert pkmn.NatDex == resultPkmn.NatDex
					if pkmn._id == None:
						continue
					pkmn.__dict__.update(resultPkmn.__dict__)
					await pkmn.save()
		except AssertionError as e:
			log.error(f"Failed to apply new stats to pokemon after battle: {e}")

	def __create_battle_summary_msg(
		self, results: battleapi.BattleResults
	) -> discord.Embed:
		embed = discord.Embed(title="Battle Results")
		embed.add_field(name="Winner", value=self.agents[results.winner].name)
		return embed

	async def __cleanup(self):
		log.debug("cleaning up completed battle")
		global battles
		idx = None
		for i, b in enumerate(battles):
			if b is self:
				idx = i
				break
		if idx == None:
			log.critical("Unable to find battle in all registered battles.")
			return
		async with battles_lock:
			del battles[idx]


battles: list[Battle] = []
battles_lock = asyncio.Lock()
