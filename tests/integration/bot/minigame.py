import sys
import asyncio
from discord import Embed, Member, Status, Message
from distest.TestInterface import TestInterface
from distest import run_dtest_bot, TestCollector
from brock_test_util import resetdb

test_collector = TestCollector()


@test_collector()
async def test_minigame(interface: TestInterface):
	await resetdb(interface)

	await interface.send_message("p!begin")
	msg: Message = await interface.wait_for_message()
	await interface.wait_for_reaction(msg)
	await msg.add_reaction("🇩")
	msg2: Message = await interface.wait_for_message()
	await interface.assert_message_contains(msg2, "Profile created")
	await asyncio.sleep(0.5)

	embed = Embed(
		title="Who's That Pokemon?",
		description="Can you guess the name of the Pokemon shown below?",
	)

	await interface.assert_reply_embed_equals(
		"p!callMinigame 25", embed, ["title", "description"]
	)
	await interface.assert_reply_contains("guess hint", "starts with the letter")
	await interface.assert_reply_contains("guess mew", "That's incorrect")
	await interface.assert_reply_contains(
		"guess pikach", "that guess was close, but not quite right"
	)

	await interface.assert_reply_embed_regex(
		"guess pikachu", {
			"title":
			"Correct!",
			"description":
			r"Nice one, <@!?\d+>, that's right! Adding Pikachu to your inventory"
		}
	)


if __name__ == "__main__":
	run_dtest_bot(sys.argv, test_collector)
