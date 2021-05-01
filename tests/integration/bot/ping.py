import sys
import asyncio
from discord import Embed, Member, Status
import discord
from distest import run_dtest_bot, TestCollector
from distest.TestInterface import TestInterface

test_collector = TestCollector()


@test_collector()
async def test_ping(interface: TestInterface):
	await interface.assert_reply_contains("p!ping", "pong")


@test_collector()
async def test_prompt_message(interface: TestInterface):
	msg: discord.Message = await interface.wait_for_reply("p!test_prompt_message")
	await interface.wait_for_reaction(msg)

	async def small_wait():
		# required to make the test less brittle
		await asyncio.sleep(0.5)
		await msg.add_reaction("🇨")

	interface.client.loop.create_task(small_wait())
	result_msg: discord.Message = await interface.wait_for_message()
	await interface.assert_message_equals(result_msg, "got: 2")


if __name__ == "__main__":
	run_dtest_bot(sys.argv, test_collector)
