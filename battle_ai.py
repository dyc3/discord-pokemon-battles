from typing import Callable
from turns import *
from pkmntypes import *
import random, typing
import logging, coloredlogs

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=log)

battle_strategy_type = Callable[[BattleContext], Turn]
strategies: dict[str, battle_strategy_type] = {}


def battle_strategy(func: battle_strategy_type):
	"""Mark a function as a battle strategy."""
	global strategies
	name = func.__name__
	log.info(f"Adding battle strategy: {name}")
	strategies[name] = func
	return func


@battle_strategy
def simple(ctx: BattleContext) -> Turn:
	"""Battle strategy that randomly uses moves."""
	target = ctx.opponents[0]
	return FightTurn(
		party=target.party,
		slot=target.slot,
		move=random.randint(0,
							len(ctx.pokemon.Moves) - 1)
	)
