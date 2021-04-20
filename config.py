"""Provides values to Brock, read from configuration sources."""
import os
from pathlib import Path

BROCK_ENVIRONMENT = os.environ.get("BROCK_ENVIRONMENT", "prod")
assert BROCK_ENVIRONMENT in [
	"dev-test", "prod"
], "BROCK_ENVIRONMENT must be set to \"dev-test\", or \"prod\""


def read_discord_token():
	"""Read the bot's token from disk."""
	token_file = Path("./token")
	if token_file.exists():
		with open("token", "r") as f:
			return "".join(f.readlines()).strip()


BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
	BOT_TOKEN = read_discord_token()
assert BOT_TOKEN != None, "BOT_TOKEN was not provided."
