import discord

class Agent():
	"""
	An handles grabbing input from the user and makes it available for the `Battle`.
	"""

	def __init__(self, user=None):
		self.user: discord.User = user


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
