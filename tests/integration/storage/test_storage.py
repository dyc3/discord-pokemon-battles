import unittest

from motor.motor_asyncio import AsyncIOMotorClient
from turns import *
from pkmntypes import *
import asyncio
import storage
from userprofile import UserProfile, load_profile
from hypothesis import given, strategies as st
import battleapi


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

	def test_profile_load(self):

		async def go():
			profile = UserProfile()
			profile.user_id = 1234
			await profile.save()
			self.assertIsNotNone(profile._id)
			self.assertIsNotNone(profile.user_id)
			loaded = await load_profile(1234)
			self.assertEqual(profile._id, loaded._id)
			self.assertEqual(profile.user_id, loaded.user_id)

		return self.loop.run_until_complete(go())

	def test_profile_with_pokemon(self):

		async def go():
			pkmn = await battleapi.generate_pokemon()
			await pkmn.save()
			profile = UserProfile()
			profile.add_pokemon(pkmn)
			await profile.save()
			self.assertIsNotNone(profile._id)
			all_pokemon = [p async for p in profile.pokemon_iter()]
			self.assertEqual(len(all_pokemon), 1)
			self.assertIsNotNone(all_pokemon[0]._id)
			self.assertEqual(all_pokemon[0]._id, pkmn._id)

		return self.loop.run_until_complete(go())

	def test_profile_no_duplicate_pokemon(self):
		"""Make sure the profile doesn't save duplicate pokemon ids."""

		async def go():
			pkmn = await battleapi.generate_pokemon()
			await pkmn.save()
			profile = UserProfile()
			profile.add_pokemon(pkmn)
			profile.add_pokemon(pkmn)
			await profile.save()
			self.assertEqual(len(profile.pokemon), 1)

		return self.loop.run_until_complete(go())


if __name__ == "__main__":
	unittest.main()
