from pkmntypes import *
import discord
from bson.objectid import ObjectId


class UserProfile:
	"""A user's profile contains all persistent data regarding a user's progress.

	:param user_id: Discord ID associated with this profile.
	:param pokemon: Object IDs of the pokemon that this user owns.
	"""

	_id: Optional[ObjectId] = None
	user_id: int = None
	pokemon: list[ObjectId] = []

	def user(self) -> discord.User:
		"""Discord user associated with this profile."""
		pass

	async def pokemon_iter(self) -> list[Pokemon]:
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
