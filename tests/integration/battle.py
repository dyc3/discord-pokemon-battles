import sys
import asyncio
from discord import Embed, Member, Status, Message
from distest.TestInterface import TestInterface
from distest import run_dtest_bot, TestCollector

test_collector = TestCollector()

@test_collector()
async def test_battle(interface: TestInterface):
	await interface.assert_reply_contains("p!challenge bot", "challenging")
	turn_msg: Message = await interface.wait_for_message()
	await interface.wait_for_reaction(turn_msg)

if __name__ == "__main__":
	run_dtest_bot(sys.argv, test_collector)
