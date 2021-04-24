import logging
from pkmntypes import BattleContext, Pokemon, Stat

log = logging.getLogger(__name__)
from PIL import Image, ImageDraw, ImageFont
import time


def get_background() -> Image.Image:
	"""Grab a battle background."""
	return Image.open("./images/battle-background-hd.png")


def offset(pos: tuple[int, int], offset: tuple[int, int]) -> tuple[int, int]:
	"""Offset xy coordinates `pos` by `offset`."""
	x, y = pos
	x2, y2 = offset
	return (x + x2, y + y2)


def render_info_box(pkmn: Pokemon) -> Image.Image:
	"""Render an info box that is shown in battle for the given pokemon."""
	font = ImageFont.truetype("./data/fonts/pokemon-gen-4-regular.ttf", 18)
	im = Image.open("./data/images/pkmn_info_box.png")
	draw = ImageDraw.Draw(im)
	name_pos = (34, 12)
	health_text_pos = (236, 54)
	draw.text(name_pos, pkmn.Name, fill=(0, 0, 0), font=font)
	draw.text(
		health_text_pos,
		f"{pkmn.CurrentHP}/{pkmn.Stats[Stat.Hp]}",
		fill=(0, 0, 0),
		font=font
	)
	return im


def visualize_battle(ctx: BattleContext) -> Image.Image:
	"""Visualize the battlecontext."""
	start_time = time.time()
	im = get_background()
	im_pkmn = ctx.pokemon.get_image()
	im.paste(im_pkmn, (350, im.height - im_pkmn.height - 50), im_pkmn)
	im_opponent = ctx.opponents[0].pokemon.get_image()
	im.paste(im_opponent, (im.width - im_opponent.width - 200, 60), im_opponent)

	info_box = render_info_box(ctx.pokemon)
	pkmn_info_box_pos = (im.width - info_box.width, im.height - info_box.height)
	im.paste(info_box, pkmn_info_box_pos, mask=info_box)

	duration = time.time() - start_time
	log.info(f"Battle visualized in {duration} seconds.")
	return im
