import logging
from pkmntypes import BattleContext

log = logging.getLogger(__name__)
from PIL import Image
import time


def get_background() -> Image:
	"""Grab a battle background."""
	return Image.open("./images/battle-background-hd.png")


def visualize_battle(ctx: BattleContext) -> Image:
	"""Visualize the battlecontext."""
	start_time = time.time()
	im = get_background()
	pkmn = ctx.pokemon.get_image()
	im.paste(pkmn, (350, im.height - pkmn.height - 50), pkmn)
	opponent = ctx.opponents[0].pokemon.get_image()
	im.paste(opponent, (im.width - opponent.width - 200, 60), opponent)
	duration = time.time() - start_time
	log.info(f"Battle visualized in {duration} seconds.")
	return im
