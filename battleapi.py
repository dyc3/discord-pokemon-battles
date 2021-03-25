
from pkmntypes import *
import aiohttp
import logging
import jsonpickle

BASE_URL = "http://api:4000"

async def create_battle(teams: list[Team]) -> dict:
	"""
	Creates a new battle from a list of teams.

	:param teams: The list of teams
	:returns: The arguments to be used to create a new instance of a `Battle`.
	"""
	assert isinstance(teams, list)
	for team in teams:
		assert isinstance(team, Team), f"each team must be type `Team`, not {type(team)}"
	logging.debug("creating battle")
	async with aiohttp.ClientSession() as session:
		async with session.post(f"{BASE_URL}/battle/new", data=jsonpickle.encode({ "teams": teams }, unpicklable=False)) as resp:
			logging.debug(f"battle created: {resp.status}")
			result = await resp.json()
			return {
				"bid": result["BattleId"],
				"active_pokemon": result["ActivePokemon"],
			}
