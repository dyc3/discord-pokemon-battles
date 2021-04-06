import unittest

from motor.motor_asyncio import AsyncIOMotorClient
from turns import *
from pkmntypes import *
import asyncio
import storage
from userprofile import UserProfile
from hypothesis import given, strategies as st


class TestStorage(unittest.TestCase):

	def setUp(self):
		self.loop = asyncio.new_event_loop()
		asyncio.set_event_loop(self.loop)
		self.client = AsyncIOMotorClient('mongodb://db/brock_test', io_loop=self.loop)
		storage._set_client(self.client)

	def tearDown(self):

		async def tearDown_async():
			await self.client.drop_database("brock_test")

		self.loop.run_until_complete(tearDown_async())
		self.loop.close()

	def test_pokemon_save(self):

		async def go():
			pkmn = Pokemon()
			await pkmn.save()
			self.assertIsNotNone(pkmn._id)

		return self.loop.run_until_complete(go())

	def test_profile_save(self):

		async def go():
			profile = UserProfile()
			await profile.save()
			self.assertIsNotNone(profile._id)

		return self.loop.run_until_complete(go())


if __name__ == "__main__":
	unittest.main()
