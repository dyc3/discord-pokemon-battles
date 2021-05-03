import sys
import asyncio
from discord import Embed, Member, Status, Message
from distest.TestInterface import TestInterface
from distest import run_dtest_bot, TestCollector
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession, AsyncIOMotorCollection, AsyncIOMotorDatabase
from brock_test_util import resetdb, ensure_profile

test_collector = TestCollector()


@test_collector()
async def test_begin_prompt_create_profile(interface: TestInterface):
	await resetdb(interface)
	await interface.send_message("p!begin")
	msg: Message = await interface.wait_for_message()
	await interface.wait_for_reaction(msg)
	await msg.add_reaction("🇩")


@test_collector()
async def test_begin_no_duplicates(interface: TestInterface):
	await resetdb(interface)
	await ensure_profile(interface)

	await interface.send_message("p!begin")
	msg3: Message = await interface.wait_for_message()
	await interface.assert_message_equals(msg3, "You've already started a profile!")


if __name__ == "__main__":
	run_dtest_bot(sys.argv, test_collector)
