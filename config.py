"""Provides values to Brock, read from configuration sources."""
import os
from pathlib import Path


def read_discord_token():
	"""Read the bot's token from disk."""
	token_file = Path("./token")
	if token_file.exists():
		with open("token", "r") as f:
			return "".join(f.readlines()).strip()


__exclude_exports__ = set(dir())

BROCK_ENVIRONMENT = os.environ.get("BROCK_ENVIRONMENT", "prod")
assert BROCK_ENVIRONMENT in [
	"dev-test", "prod"
], "BROCK_ENVIRONMENT must be set to \"dev-test\", or \"prod\""

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
	BOT_TOKEN = read_discord_token()
assert BOT_TOKEN != None, "BOT_TOKEN was not provided."

BATTLE_API_BASE_URL = os.environ.get("BATTLE_API_BASE_URL", "http://api:4000")

__all__ = [x for x in dir() if not x.startswith("_") or x not in __exclude_exports__]
