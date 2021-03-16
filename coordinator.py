import logging
import aiohttp
import discord
from turns import *
import util

def set_bot(b):
	global bot
	bot = b

class Agent():
	"""
	An handles grabbing input from the user or AI and makes it available for the `Battle`.
	"""

	def __init__(self, user=None, bot=None):
		self.user: discord.User = user
		self.bot: str = bot

	async def get_turn(self, context) -> Turn:
		logging.debug(f"getting turn from {self}")
		if self.bot != None:
			return FightTurn(party=0, slot=0, move=0)
		if self.user != None:
			return await util.prompt_for_turn(bot, self.user, context)

	def __str__(self):
		if self.bot != None:
			return f"Agent<Bot: {self.bot}>"
		if self.user != None:
			return f"Agent<User: {self.user.name}>"
		return f"Agent<invalid>"

class Battle():
	def __init__(self, bid):
		self.bid = bid
		self.agents = []
		self.transactions = []

	def add_user(self, user: discord.User):
		assert user != None
		assert isinstance(user, discord.User) or isinstance(user, discord.Member), f"user should not be {type(user)}"
		self.agents.append(Agent(user=user))

	def add_bot(self, botname: str):
		self.agents.append(Agent(bot=botname))

	async def queue_turns(self):
		async with aiohttp.ClientSession() as session:
			for i, agent in enumerate(self.agents):
				# FIXME: this breaks when
				async with session.get(f"http://api:4000/battle/context?id={self.bid}&party={i}&slot=0") as resp:
					context = await resp.json()
				turn = await agent.get_turn(context)
				logging.debug(f"posting turn {turn} from {agent}")
				if not turn:
					# HACK: fucking async
					turn = FightTurn(party=0, slot=0, move=0)
				async with session.post(f"http://api:4000/battle/act?id={self.bid}&agent={i}", data=turn.toJSON()) as resp:
					pass

	async def simulate(self):
		"""
		Simulate the entire battle. Asynchronously blocks until the battle is completed.
		"""
		while True:
			async with aiohttp.ClientSession() as session:
				logging.debug("asking agents for turns")
				await self.queue_turns()
				logging.debug("simulating round")
				async with session.get(f"http://api:4000/battle/simulate?id={self.bid}") as resp:
					# TODO: change battle API to give correct content type
					results = await resp.json()
			self.transactions += results["Transactions"]
			if results["Ended"]:
				break

battles = [
	Battle(0) # temporary
]
