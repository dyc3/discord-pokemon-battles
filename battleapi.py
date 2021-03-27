
from pkmntypes import *
import aiohttp
import logging
import jsonpickle
from pkmntypes import *
from turns import *

BASE_URL = "http://api:4000"

async def generate_pokemon() -> dict:
	"""Get a randomly generated pokemon from the API.
	"""
	async with aiohttp.ClientSession() as session:
		async with session.get(f"{BASE_URL}/pokedex/generate") as resp:
			return await resp.json()

async def create_battle(teams: list[Team]) -> dict:
	"""
	Creates a new battle from a list of teams.

	:param teams: The list of teams
	:returns: The parameters to be applied to an instance of a `Battle`.
	"""
	assert isinstance(teams, list)
	for team in teams:
		assert isinstance(team, Team), f"each team must be type `Team`, not {type(team)}"
	logging.debug("creating battle")
	async with aiohttp.ClientSession() as session:
		async with session.post(f"{BASE_URL}/battle/new", data=jsonpickle.encode({ "teams": teams }, unpicklable=False)) as resp:
			logging.debug(f"battle created: {resp.status}")
			result = await resp.json(content_type=None)
			return {
				"bid": result["BattleId"],
				"active_pokemon": result["ActivePokemon"],
			}

async def get_battle_context(battle_id: int, target: int) -> dict:
	"""Get the battle context for a given target.

	:returns: The battle context.
	"""
	logging.debug(f"getting battle context: battle={battle_id} target={target}")
	async with aiohttp.ClientSession() as session:
		async with session.get(f"{BASE_URL}/battle/context?id={battle_id}&target={target}") as resp:
			result = await resp.json()
	return result

async def submit_turn(battle_id: int, target: int, turn: Turn):
	"""Submit a turn for the given target.
	"""
	logging.debug(f"submitting turn: battle={battle_id} target={target} turn={type(turn)}")
	async with aiohttp.ClientSession() as session:
		async with session.post(f"{BASE_URL}/battle/act?id={battle_id}&target={target}", data=turn.toJSON()) as resp:
			pass

async def simulate(battle_id: int) -> dict:
	"""Simulate a round of the battle, and get the results of the round.

	:returns: The results of the round.
	"""
	logging.debug(f"simulating round: battle={battle_id}")
	async with aiohttp.ClientSession() as session:
		async with session.get(f"{BASE_URL}/battle/simulate?id={battle_id}") as resp:
			result = await resp.json()
	return result
