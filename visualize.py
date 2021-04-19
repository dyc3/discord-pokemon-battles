import logging
from pkmntypes import BattleContext

log = logging.getLogger(__name__)
from PIL import Image


def get_background() -> Image:
	"""Grab a battle background."""
	return Image.open("./images/battle-background-hd.png")


def visualize_battle(ctx: BattleContext) -> Image:
	"""Visualize the battlecontext."""
	im = Image.new("RGB", (1280, 720), "white")
	im.paste(get_background())
	pkmn = ctx.pokemon.get_image()
	im.paste(pkmn, (350, im.height - pkmn.height - 50), pkmn)
	opponent = ctx.opponents[0].pokemon.get_image()
	im.paste(opponent, (im.width - opponent.width - 200, 60), opponent)
	return im
