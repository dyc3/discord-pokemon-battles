from typing import AsyncIterator
from pkmntypes import *
import discord
from bson.objectid import ObjectId
import logging, coloredlogs
import datetime

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=log)


class UserProfile:
	"""A user's profile contains all persistent data regarding a user's progress.

	:param user_id: Discord ID associated with this profile.
	:param pokemon: Object IDs of the pokemon that this user owns.
	"""

	_id: Optional[ObjectId] = None
	user_id: int = 0
	pokemon: list[ObjectId]
	created_at: datetime.datetime

	def __init__(self):
		self.pokemon = []
		self.created_at = datetime.datetime.now()

	def user(self) -> discord.User:
		"""Discord user associated with this profile."""
		if self.user_id in user_cache:
			return user_cache[self.user_id]

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
		embed.set_image(url=str(self.user().avatar_url))
		embed.title = self.user().name
		date = self.created_at
		embed.description = f"This account was created on {date.strftime('%x')}"
		return embed


async def load_profile(discord_id: int) -> Optional[UserProfile]:
	"""Load a :class:`UserProfile` by discord user id. If no profile exists, it returns none."""
	import storage
	doc = await storage.user_profiles().find_one({"user_id": discord_id})
	if not doc:
		return None
	profile = UserProfile()
	profile.__dict__.update(**doc)
	return profile


user_cache: dict[int, discord.User] = {}


def add_user_to_cache(user: discord.User) -> None:
	"""Add the given user to our cache of user objects, so we can look users up by user ID later. This is required so we don't have to use any Privileged Gateway Intents."""
	log.debug(f"Adding {user} to cache")
	user_cache[user.id] = user
