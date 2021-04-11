import sys
import asyncio
from discord import Embed, Member, Status, Message
from distest.TestInterface import TestInterface
from distest import run_dtest_bot, TestCollector

test_collector = TestCollector()

#BUG these tests wont work unless we consistently get the same result from generate_pokemon()
# can we do that by setting the seed before testing?


@test_collector()
async def test_minigame_correct_guess(interface: TestInterface):
	await interface.assert_reply_contains(
		"p!minigame", "Can you guess the name of the Pokemon shown below?"
	)
	image_message: Message = await interface.wait_for_message()
	disclaimer_message: Message = await interface.wait_for_message()
	await interface.assert_message_has_image(image_message)
	await interface.assert_message_contains(
		disclaimer_message, "Please prefix all guesses"
	)
	await interface.assert_reply_contains("guess pichu", "that's correct")


@test_collector()
async def test_minigame_incorrect_guess(interface: TestInterface):
	await interface.assert_reply_contains(
		"p!minigame", "Can you guess the name of the Pokemon shown below?"
	)
	image_message: Message = await interface.wait_for_message()
	disclaimer_message: Message = await interface.wait_for_message()
	await interface.assert_message_has_image(image_message)
	await interface.assert_message_contains(
		disclaimer_message, "Please prefix all guesses"
	)
	await interface.assert_reply_contains("guess mew", "incorrect")
	# is there a way to cancel the command you are testing
	# since the minigame has acquired the lock and doesn't release it until a correct guess is made,
	# i could see this getting in the way of other tests


if __name__ == "__main__":
	run_dtest_bot(sys.argv, test_collector)