import logging
import asyncio
import aiohttp
import functools
import discord
from turns import *
import util
import battleapi
from pkmntypes import *

log = logging.getLogger(__name__)


def set_bot(b):
	"""Set the bot that the coordinator should use."""

	global bot
	bot = b


class Agent():
	"""An handles grabbing input from the user or AI and makes it available for the :class:`Battle`."""

	def __init__(self, user=None, bot=None):
		self.user: discord.User = user
		self.bot: str = bot

	async def get_turn(self, context, original_channel: discord.TextChannel) -> Turn:
		"""Get a turn from the Agent."""

		log.debug(f"getting turn from {self}")
		if self.bot != None:
			return FightTurn(party=0, slot=0, move=0)
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


class Battle():
	"""A Pokemon battle. Gathers user input and manages the simulation via the battle api."""

	def __init__(self, **kwargs):
		self.bid: int = None
		self.active_pokemon: int = None
		self.agents = []
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
			turn = await agent.get_turn(context, self.original_channel)
			log.debug(f"posting turn {turn} from {agent}")
			await battleapi.submit_turn(self.bid, i, turn)

		await asyncio.gather(*[_do(i, agent) for i, agent in enumerate(self.agents)])

	async def simulate(self):
		"""Simulate the entire battle. Asynchronously blocks until the battle is completed."""

		while True:
			log.debug("asking agents for turns")
			await self.queue_turns()
			log.debug("simulating round")
			results = await battleapi.simulate(self.bid)
			self.transactions += results.transactions
			if results.ended:
				break
		log.info(f"Battle between {self.agents} concluded")
		results = await battleapi.get_results(self.bid)
		if self.original_channel:
			await self.original_channel.send(
				embed=self.__create_battle_summary_msg(results)
			)
		await self.apply_post_battle_updates(results)

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
					pkmn.__dict__.update(resultPkmn.__dict__)
					await pkmn.save()
		except AssertionError as e:
			log.error(f"Failed to apply new stats to pokemon after battle: {e}")

	def __create_battle_summary_msg(
		self, results: battleapi.BattleResults
	) -> discord.Embed:
		embed = discord.Embed(title="Battle Results")
		if self.agents[results.winner].user:
			embed.add_field(name="Winner", value=self.agents[results.winner].user)
		else:
			embed.add_field(name="Winner", value=self.agents[results.winner].bot)
		return embed


battles: list[Battle] = []
