import asyncio
from pkmntypes import Pokemon
from typing import Union
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession, AsyncIOMotorCollection, AsyncIOMotorDatabase
import logging
from userprofile import UserProfile

log = logging.getLogger(__name__)
client: AsyncIOMotorClient = AsyncIOMotorClient('mongodb://db/brock')
db: AsyncIOMotorDatabase = client.brock


def _set_client(new_client: AsyncIOMotorClient):
	"""Manually set the mongodb client that `storage` should use. Only to be used in tests."""

	global client, db
	client = new_client
	db = client.brock_test


def pokemon() -> AsyncIOMotorCollection:
	"""Get the Pokemon collection to be able to interact with the database."""
	return db.pokemon


def user_profiles() -> AsyncIOMotorCollection:
	"""Get the user profile collection to be able to interact with the database."""
	return db.profiles


async def save_object(
	obj: Union[Pokemon, UserProfile], session: AsyncIOMotorClientSession = None
):
	"""Save the given object to the database. If `_id` is not set, a new entry will be created and the object's `_id` will be updated. If `_id` is set, it will try to update the document with that ID.

	:param session: The database session to use to save the pokemon. If not provided, it will not be used.

	:raises:
		TypeError: The type of object provided is not allowed to be saved in the database.
	"""
	if isinstance(obj, Pokemon):
		coll = pokemon()
	elif isinstance(obj, UserProfile):
		coll = user_profiles()
	else:
		raise TypeError(f"Invalid type for obj: {type(obj)}")
	if obj._id != None:
		result = await coll.update_one(
			{'_id': obj._id}, {'$set': obj.__dict__}, session=session
		)
		log.debug(f"Updated {type(obj)} ({result.modified_count} modified)")
	else:
		result = await coll.insert_one(
			{k: v
				for k, v in obj.__dict__.items() if k != "_id"}, session=session
		)
		obj._id = result.inserted_id
		log.debug(f"Inserted {type(obj)} ({obj._id})")
