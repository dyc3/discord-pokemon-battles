from coordinator import Battle
import unittest

from motor.motor_asyncio import AsyncIOMotorClient
from turns import *
from pkmntypes import *
import asyncio
import storage
from userprofile import UserProfile, load_profile
from hypothesis import given, strategies as st
import battleapi
import util


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

	def test_post_battle_apply(self):

		async def go():
			pkmn = await battleapi.generate_pokemon()
			pkmn2 = await battleapi.generate_pokemon()
			await pkmn.save()
			await pkmn2.save()
			p1 = Party(pokemon=[pkmn])
			p2 = Party(pokemon=[pkmn2])
			teams = util.build_teams_single(p1, p2)
			battle = Battle(teams=teams)
			import copy
			p1next = copy.deepcopy(p1)
			p2next = copy.deepcopy(p2)
			p1next.pokemon[0]._id = None
			p1next.pokemon[0].EVs = [21, 31, 27, 6, 11, 12]
			p2next.pokemon[0]._id = None
			p2next.pokemon[0].CurrentHP = 0
			results = battleapi.BattleResults(1, [])
			results.parties = [p1next, p2next]
			await battle.apply_post_battle_updates(results)
			self.assertIsNotNone(p1.pokemon[0]._id)
			self.assertIsNotNone(p2.pokemon[0]._id)
			self.assertListEqual(p1.pokemon[0].EVs, p1next.pokemon[0].EVs)
			self.assertEqual(p2.pokemon[0].CurrentHP, p2next.pokemon[0].CurrentHP)

		return self.loop.run_until_complete(go())


if __name__ == "__main__":
	unittest.main()
