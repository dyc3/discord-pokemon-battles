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
	available_moves = [
		i for i, move in enumerate(ctx.pokemon.Moves) if move.current_pp > 0
	]
	return FightTurn(
		party=target.party, slot=target.slot, move=random.choice(available_moves)
	)


@battle_strategy
def inflicter(ctx: BattleContext):
	"""Battle strategy that uses status inflicting moves if the opponent does not have a status condition, and then damage dealing moves."""
	status_moves = list(
		filter(lambda x: x.ailment.value > 0 or x.flinch_chance > 0, ctx.pokemon.Moves)
	)
	non_status_moves = list(filter(lambda x: x.category != 0, ctx.pokemon.Moves))

	target = ctx.opponents[0]
	if target.pokemon.StatusEffects.value == 0 and len(status_moves) > 0:
		log.debug("opponent doesn't have any status condition, attempting to inflict one")
		move = random.choice(status_moves)
	elif len(non_status_moves) > 0:
		move = random.choice(non_status_moves)
	else:
		move = random.choice(ctx.pokemon.Moves)
	return ctx.fight(target, move)
