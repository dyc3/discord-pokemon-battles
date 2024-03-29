from typing import Generator, Iterable, Sequence, Union, Optional, Any
from pkmntypes import *
import aiohttp
import jsonpickle
from pkmntypes import *
from turns import *
import os
import config
import logging, coloredlogs

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=log)

BASE_URL = config.BATTLE_API_BASE_URL

__exclude_exports__ = set(dir())


class BattleRoundResults:
	"""Results of a single round of battle."""

	def __init__(self, **kwargs) -> None:
		self.transactions: list[Transaction] = [
			Transaction(**t) for t in kwargs.get("Transactions", []) or []
		]
		self.ended: bool = kwargs["Ended"]


async def generate_pokemon(
	natdex: Optional[int] = None,
	level: Optional[int] = None,
	moves: Optional[list[int]] = None
) -> Pokemon:
	"""Get a randomly generated pokemon from the API."""
	params: dict[str, Any] = {}
	if natdex:
		params["natdex"] = natdex
	if level:
		params["level"] = level
	if moves:
		params["moves"] = ','.join([str(m) for m in moves])
	async with aiohttp.ClientSession() as session:
		url = f"{BASE_URL}/pokedex/generate"
		async with session.get(url, params=params) as resp:
			result = await resp.json()
			return Pokemon(**result)


async def create_battle(teams: list[Team]) -> dict[str, Any]:
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


class BattleResults:
	"""Results of a concluded battle."""

	winner: int
	parties: list[Party]

	def __init__(self, winner: int, parties: list[dict[str, Any]]):
		self.winner = winner
		self.parties = [Party(pokemon=p["Pokemon"]) for p in parties]


async def get_results(battle_id: int) -> BattleResults:
	"""Get the results of a battle that has finished."""
	async with aiohttp.ClientSession() as session:
		async with session.get(f"{BASE_URL}/battle/results?id={battle_id}") as resp:
			log.debug(f"battle results: {resp.status}")
			result = await resp.json()
	return BattleResults(result["Winner"], result["Parties"])


__all__ = [x for x in dir() if not x.startswith("_") or x not in __exclude_exports__]
