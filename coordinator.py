import discord
from turns import *
import bot

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
			return await bot.prompt_for_turn(self.user, context)

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
		self.agents.push(Agent(user=user))

battles = [
	Battle(0) # temporary
]
