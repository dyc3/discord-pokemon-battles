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
	font_big = ImageFont.truetype("./data/fonts/pokemon-gen-4-regular.ttf", 18)
	im = Image.open("./data/images/pkmn_info_box.png")
	draw = ImageDraw.Draw(im)
	name_pos = (34, 12)
	health_text_pos = (136, 51)
	draw.text(name_pos, pkmn.Name, fill=(0, 0, 0), font=font_big)
	font_sm = ImageFont.truetype("./data/fonts/pokemon-gen-4-regular.ttf", 14)
	draw.text(
		health_text_pos,
		f"{pkmn.CurrentHP}/{pkmn.Stats[Stat.Hp]}",
		fill=(0, 0, 0),
		font=font_sm
	)
	hp_bar_left, hp_bar_y = (136, 42)
	hp_bar_width, hp_bar_height = (95, 6)
	adjusted_hp_width = int((pkmn.CurrentHP / pkmn.Stats[Stat.Hp]) * hp_bar_width)
	draw.line(
		[(hp_bar_left, hp_bar_y), (hp_bar_left + adjusted_hp_width, hp_bar_y)],
		fill=(48, 181, 53),
		width=hp_bar_height
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
	info_box_scale = 2.75
	info_box_size = (
		int(info_box.width * info_box_scale), int(info_box.height * info_box_scale)
	)
	info_box = info_box.resize(info_box_size, Image.NEAREST)
	pkmn_info_box_pos = (im.width - info_box_size[0], im.height - info_box_size[1])
	im.paste(info_box, pkmn_info_box_pos, mask=info_box)

	info_box_opponent = render_info_box(ctx.opponents[0].pokemon)
	info_box_opponent_size = (
		int(info_box_opponent.width * info_box_scale),
		int(info_box_opponent.height * info_box_scale)
	)
	info_box_opponent = info_box_opponent.resize(info_box_opponent_size, Image.NEAREST)
	pkmn_info_box_pos = (
		im.width - info_box_opponent_size[0], im.height - info_box_opponent_size[1]
	)
	im.paste(info_box_opponent, (0, 0), mask=info_box)

	duration = time.time() - start_time
	log.info(f"Battle visualized in {duration} seconds.")
	return im
