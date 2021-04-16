from typing import AsyncIterator
from pkmntypes import *
import discord
from bson.objectid import ObjectId


class UserProfile:
	"""A user's profile contains all persistent data regarding a user's progress.

	:param user_id: Discord ID associated with this profile.
	:param pokemon: Object IDs of the pokemon that this user owns.
	"""

	_id: Optional[ObjectId] = None
	user_id: int = 0
	pokemon: list[ObjectId]

	def __init__(self):
		self.pokemon = []

	def user(self) -> discord.User:
		"""Discord user associated with this profile."""
		pass

	async def pokemon_iter(self) -> AsyncIterator[Pokemon]:
		"""Grabs pokemon from the database and provides them as an async generator."""
		import storage # avoid circular import
		for oid in self.pokemon:
			# TODO: replace with helper function
			doc = await storage.pokemon().find_one({"_id": oid})
			yield Pokemon(**doc)

	async def save(self, session: AsyncIOMotorClientSession = None):
		"""Alias for `storage.save_object(profile)`."""
		import storage # avoid circular import
		await storage.save_object(self, session=session)

	def add_pokemon(self, pokemon: Pokemon):
		"""Add pokemon to user profile."""
		if pokemon._id in self.pokemon:
			return
		self.pokemon.append(pokemon._id)

	def get_embed(self) -> discord.Embed:
		"""Get a pretty embed to display a UserProfile."""
		embed = discord.Embed()
		embed.title = "profile"
		embed.description = "profile description"
		return embed


async def load_profile(discord_id: int) -> UserProfile:
	"""Load a :class:`UserProfile` by discord user id."""
	import storage
	doc = await storage.user_profiles().find_one({"user_id": discord_id})
	if not doc:
		return None
	profile = UserProfile()
	profile.__dict__.update(**doc)
	return profile
