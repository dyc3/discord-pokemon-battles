from pkmntypes import *
import aiohttp
import logging
import jsonpickle
from pkmntypes import *
from turns import *
import os

log = logging.getLogger(__name__)

BASE_URL = os.environ.get("BATTLE_API_BASE_URL", "http://api:4000")


class BattleRoundResults:
	"""Results of a single round of battle."""

	def __init__(self, **kwargs) -> None:
		self.transactions: list[Transaction] = [
			Transaction(**t) for t in kwargs["Transactions"]
		]
		self.ended: bool = kwargs["Ended"]


async def generate_pokemon(params: dict = {}) -> Pokemon:
	"""Get a pokemon from the API, optionally passing a dict which defines the pokemon to be generated.

	Any parameters that are omitted will be randomized.
	Calling the function with no arguments will generate a completely random pokemon.
	"""
	async with aiohttp.ClientSession() as session:
		async with session.get(f"{BASE_URL}/pokedex/generate", params=params) as resp:
			result = await resp.json()
			return Pokemon(**result)


async def create_battle(teams: list[Team]) -> dict:
	"""Create a new battle from a list of teams.

	:param teams: The list of teams
	:returns: The parameters to be applied to an instance of a `Battle`.
	"""
	assert isinstance(teams, list)
	for team in teams:
		assert isinstance(team, Team), f"each team must be type `Team`, not {type(team)}"
	log.debug("creating battle")
	async with aiohttp.ClientSession() as session:
		async with session.post(
			f"{BASE_URL}/battle/new",
			data=jsonpickle.encode({"teams": teams}, unpicklable=False)
		) as resp:
			log.debug(f"battle created: {resp.status}")
			result = await resp.json(content_type=None)
			return {
				"bid": result["BattleId"],
				"active_pokemon": result["ActivePokemon"],
			}


async def get_battle_context(battle_id: int, target: int) -> BattleContext:
	"""Get the battle context for a given target.

	:returns: The battle context.
	"""
	log.debug(f"getting battle context: battle={battle_id} target={target}")
	async with aiohttp.ClientSession() as session:
		async with session.get(
			f"{BASE_URL}/battle/context?id={battle_id}&target={target}"
		) as resp:
			result = await resp.json()
	return BattleContext(**result)


async def submit_turn(battle_id: int, target: int, turn: Turn):
	"""Submit a turn for the given target."""
	log.debug(f"submitting turn: battle={battle_id} target={target} turn={type(turn)}")
	async with aiohttp.ClientSession() as session:
		async with session.post(
			f"{BASE_URL}/battle/act?id={battle_id}&target={target}", data=turn.toJSON()
		) as resp:
			pass


async def simulate(battle_id: int) -> BattleRoundResults:
	"""Simulate a round of the battle, and get the results of the round.

	:returns: The results of the round.
	"""
	log.debug(f"simulating round: battle={battle_id}")
	async with aiohttp.ClientSession() as session:
		async with session.get(f"{BASE_URL}/battle/simulate?id={battle_id}") as resp:
			result = await resp.json()
	return BattleRoundResults(**result)
