from re import L
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession, AsyncIOMotorCollection, AsyncIOMotorDatabase
from distest.TestInterface import TestInterface


async def resetdb(interface: TestInterface):
	client: AsyncIOMotorClient = AsyncIOMotorClient('mongodb://db/brock_test')
	client.drop_database("brock_test")
	await interface.assert_reply_contains("p!use_test_db", "Using database")


async def ensure_profile(interface: TestInterface):
	await interface.assert_reply_equals("p!ensure_profile", "OK")
