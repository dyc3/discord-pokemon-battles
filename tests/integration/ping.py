import sys
import asyncio
from discord import Embed, Member, Status
from distest import TestInterface
from distest import run_dtest_bot, TestCollector

test_collector = TestCollector()

@test_collector()
async def test_ping(interface):
	await interface.assert_reply_contains("p!ping", "pong")

if __name__ == "__main__":
	run_dtest_bot(sys.argv, test_collector)
