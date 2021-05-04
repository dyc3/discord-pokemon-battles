import asyncio
import datetime
import jsonpickle
from pkmntypes import Pokemon
from typing import OrderedDict, Union
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession, AsyncIOMotorCollection, AsyncIOMotorDatabase
import logging, coloredlogs
from userprofile import UserProfile
from bson.objectid import ObjectId

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=log)
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
	pickler = jsonpickle.pickler.Pickler(unpicklable=False, make_refs=False)

	def pickle(o):

		def one(so):
			if isinstance(so, (int, float, bool, str, datetime.datetime, ObjectId)):
				return so
			else:
				return pickler.flatten(so)

		if hasattr(o, "__dict__"):
			pobj = {}
			for k, v in o.__dict__.items():
				if k == "_id":
					continue
				if isinstance(v, list):
					pobj[k] = [pickle(x) for x in v]
				else:
					pobj[k] = one(v)
			return pobj
		else:
			return one(o)

	pickled_obj = pickle(obj)
	log.debug(f"Pickled {type(obj)} into {pickled_obj}")
	if obj._id != None:
		result = await coll.update_one(
			{'_id': obj._id}, {'$set': pickled_obj}, session=session
		)
		log.debug(f"Updated {type(obj)} ({result.modified_count} modified)")
	else:
		result = await coll.insert_one(pickled_obj, session=session)
		obj._id = result.inserted_id
		log.debug(f"Inserted {type(obj)} ({obj._id})")


async def load_pokemon(id: ObjectId) -> Pokemon:
	"""Get pokemon from the database by its ObjectId.

	:param id: The id of the pokemon the user is trying to retrieve

	:raises:
		Exception: The pokemon with the supplied id cannot be found/does not exist

	:returns: Pokemon
	"""
	result = await pokemon().find_one({'_id': id})
	if result == None:
		raise Exception(f"No pokemon found with id: {id}")
	return Pokemon(**result)


async def set_validators():
	"""Set up mongodb validators for collections."""
	log.info("Setting validator for profiles")
	result = await db.command(
		OrderedDict(
			[
				("collMod", "profiles"),
				(
					"validator", {
						"$jsonSchema": {
							"bsonType": "object",
							"required": ["user_id"],
							"properties": {
								"user_id": {
									"bsonType": "long",
								},
								"created_at": {
									"bsonType": "date",
								},
							}
						}
					}
				),
				("validationLevel", "strict"),
			]
		)
	)
	log.debug(f"set validator result: {result}")
