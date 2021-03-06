import sys
import asyncio
from discord import Embed, Member, Status, Message
from distest.TestInterface import TestInterface
from distest import run_dtest_bot, TestCollector
from brock_test_util import resetdb

test_collector = TestCollector()


@test_collector()
async def test_turn_prompt_should_have_reactions(interface: TestInterface):
	await resetdb(interface)
	await interface.send_message("p!challenge bot")
	await interface.wait_for_message()
	turn_msg: Message = await interface.wait_for_message()
	await interface.wait_for_reaction(turn_msg)


@test_collector()
async def test_turn_prompt_content(interface: TestInterface):
	await resetdb(interface)
	await interface.send_message("p!challenge bot")
	await interface.wait_for_message()
	turn_msg: Message = await interface.wait_for_message()
	await interface.assert_message_equals(turn_msg, "Select a move")
	await interface.assert_embed_regex(
		turn_msg, {
			"title": r"[A-Z][a-z]+",
			"description": r"\d+ HP ((<:[a-z]+:\d+>|\[[A-Z][a-z]\])\s?)+",
		}
	)


if __name__ == "__main__":
	run_dtest_bot(sys.argv, test_collector)
