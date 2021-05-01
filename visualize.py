import logging
from os import name
from typing import Union
from pkmntypes import BattleContext, Pokemon, Stat

log = logging.getLogger(__name__)
from PIL import Image, ImageDraw, ImageFont
import time

hp_bar_colors = [
	(48, 181, 53), # green
	(255, 203, 5), # yellow
	(227, 0, 0), # red
]
types_conditions_atlas = Image.open(
	"./data/images/types-conditions.png"
) # to avoid unnecessary file operations


def get_background() -> Image.Image:
	"""Grab a battle background."""
	return Image.open("./images/battle-background-hd.png")


def offset(pos: tuple[int, int], offset: tuple[int, int]) -> tuple[int, int]:
	"""Offset xy coordinates `pos` by `offset`."""
	x, y = pos
	x2, y2 = offset
	return (x + x2, y + y2)


def scale(pos: tuple[Union[int, float], Union[int, float]],
			multiplier: int) -> tuple[int, int]:
	"""Scale xy coordinates `pos` by `multiplier`."""
	x, y = pos
	return (round(x * multiplier), round(y * multiplier))


def get_status_condition_img(status: int) -> Image.Image:
	"""Get the status condition badge to display.

	:param status: Non-volatile status condition.
	"""
	assert status <= 0b111, f"Only takes non-volatile status conditions, got {status:b}"
	row_size = 8
	column_size = 32
	start_y_px = 96
	# map the status condition we get from the battle api into
	# the index of the status condition in the order as they appear
	# on the image
	idx = {
		1: 4,
		2: 3,
		3: 1,
		4: 0,
		5: 0,
		6: 2,
	}[status]
	x = column_size * (idx % 4)
	y = start_y_px + (row_size * (idx // 4))
	shave = 6
	return types_conditions_atlas.copy().crop(
		(x + shave, y, x + column_size - shave, y + row_size)
	)


def render_info_box(pkmn: Pokemon, is_opponent=False, size=1) -> Image.Image:
	"""Render an info box that is shown in battle for the given pokemon."""
	text_color = (72, 72, 72)
	if not is_opponent:
		template = "./data/images/pkmn_info_box.png"
		name_pos = (34, 12)
		hp_bar_left, hp_bar_y = (136, 42.4)
	else:
		template = "./data/images/pkmn_info_box_opponent.png"
		name_pos = (8, 12)
		hp_bar_left, hp_bar_y = (102, 42.4)
	name_pos = scale(name_pos, size)
	hp_bar_left, hp_bar_y = scale((hp_bar_left, hp_bar_y), size)
	hp_bar_width, hp_bar_height = scale((96, 6), size)
	health_text_pos = scale((136, 51), size)

	font_big = ImageFont.truetype(
		"./data/fonts/pokemon-gen-4-regular.ttf", int(18 * size)
	)
	im = Image.open(template)
	im = im.resize((int(im.width * size), int(im.height * size)), Image.NEAREST)
	draw = ImageDraw.Draw(im)
	draw.text(name_pos, pkmn.Name, fill=text_color, font=font_big)
	if pkmn.Gender > 0:
		if pkmn.Gender == 1:
			gender_color = (242, 95, 47)
			gender_text = "♀"
		elif pkmn.Gender == 2:
			gender_color = (52, 99, 211)
			gender_text = "♂"
		w = draw.textlength(pkmn.Name, font=font_big)
		draw.text(offset(name_pos, (w, 0)), gender_text, font=font_big, fill=gender_color)
	font_sm = ImageFont.truetype("./data/fonts/pokemon-gen-4-regular.ttf", int(14 * size))
	level_text = f"Lv{pkmn.Level}"
	level_text_width = draw.textlength(level_text, font=font_sm)
	level_pos = offset((hp_bar_left + hp_bar_width, name_pos[1]), (-level_text_width, 0))
	draw.text(
		level_pos,
		level_text,
		fill=text_color,
		font=font_sm,
	)

	if not is_opponent:
		draw.text(
			health_text_pos,
			f"{pkmn.CurrentHP}/{pkmn.Stats[Stat.Hp]}",
			fill=text_color,
			font=font_sm
		)
	hp_percent = pkmn.CurrentHP / pkmn.Stats[Stat.Hp]
	adjusted_hp_width = int(hp_percent * hp_bar_width)
	if hp_percent > .5:
		hp_color = hp_bar_colors[0]
	elif hp_percent > .2:
		hp_color = hp_bar_colors[1]
	else:
		hp_color = hp_bar_colors[2]
	draw.line(
		[(hp_bar_left, hp_bar_y), (hp_bar_left + adjusted_hp_width, hp_bar_y)],
		fill=hp_color,
		width=hp_bar_height
	)

	# status conditions
	if (status := pkmn.StatusEffects & 0b111) > 0:
		cond = get_status_condition_img(status)
		cond = cond.resize(
			(int(cond.width * size * 1.5), int(cond.height * size * 1.5)), Image.NEAREST
		)
		status_pos = (name_pos[0], hp_bar_y - 18)
		im.paste(cond, status_pos, mask=cond)
	return im


def visualize_battle(ctx: BattleContext) -> Image.Image:
	"""Visualize the battlecontext."""
	start_time = time.time()
	im = get_background()
	im_pkmn = ctx.pokemon.get_image()
	im.paste(im_pkmn, (350, im.height - im_pkmn.height - 50), im_pkmn)
	im_opponent = ctx.opponents[0].pokemon.get_image()
	im.paste(im_opponent, (im.width - im_opponent.width - 200, 60), im_opponent)

	info_box_scale = 2.75
	info_box = render_info_box(ctx.pokemon, size=info_box_scale)
	pkmn_info_box_pos = (im.width - info_box.width, im.height - info_box.height)
	im.paste(info_box, pkmn_info_box_pos, mask=info_box)

	info_box_opponent = render_info_box(
		ctx.opponents[0].pokemon, is_opponent=True, size=info_box_scale
	)
	pkmn_info_box_pos = (
		im.width - info_box_opponent.width, im.height - info_box_opponent.height
	)
	im.paste(info_box_opponent, (0, 0), mask=info_box_opponent)

	duration = time.time() - start_time
	log.info(f"Battle visualized in {duration} seconds.")
	return im
