import asyncio
import json
import aiohttp
import logging
import discord
from discord.ext import commands
from discord.message import Message
import serve, coordinator

bot = commands.Bot(command_prefix='p!')

@bot.command()
async def ping(ctx: commands.Context):
	await ctx.send('pong')

@bot.command()
async def sim(ctx: commands.Context, bid: str):
	msg: Message = await ctx.send(f"Simulating battle {bid}...")
	async with aiohttp.ClientSession() as session:
		async with session.get(f"http://api:4000/battle/simulate?id={bid}") as resp:
			if resp.status == 200:
				print("simulate done")
				results = await resp.json()
				results = json.loads(await resp.read())
				print(f"got {len(results['Transactions'])} transactions")
				await msg.edit(content=f"Round Results: Processed {len(results['Transactions'])}")
			else:
				await msg.edit(f"Simulation failed: got {resp.status} from service")

@bot.command()
async def challenge(ctx: commands.Context, opponent: str):
	await ctx.send(f"<@!{ctx.author.id}> challenging {opponent}")
	coordinator.battles[0].add_user(ctx.author)
	if opponent.startswith("<@!") and opponent.endswith(">"):
		user = ctx.message.mensions[0]
		coordinator.battles[0].add_user(user)
	else:
		coordinator.battles[0].add_bot(opponent)

@bot.command()
async def turn(ctx: commands.Context):
	# HACK: hardcoded battle context
	turn = await prompt_for_turn(ctx.author, {
			"Battle": {
				"Weather": 0,
				"ShiftSet": False,
				"State": 1
			},
			"Pokemon": {
				"Name": "Mew",
				"NatDex": 151,
				"Level": 6,
				"TotalExperience": 179,
				"Gender": 0,
				"IVs": [3, 1, 1, 4, 0, 3],
				"EVs": [7, 24, 41, 11, 3, 20],
				"Nature": 5,
				"Stats": [28, 17, 17, 17, 17, 17],
				"StatModifiers": [0, 0, 0, 0, 0, 0, 0, 0, 0],
				"StatusEffects": 0,
				"CurrentHP": 26,
				"Moves": [{
					"ID": 447,
					"Name": "Grass Knot",
					"Type": 2048,
					"Category": 2,
					"Targets": 10,
					"CurrentPP": 20,
					"MaxPP": 20,
					"Priority": 0,
					"Power": 0,
					"Accuracy": 100
				}, {
					"ID": 449,
					"Name": "Judgment",
					"Type": 1,
					"Category": 2,
					"Targets": 10,
					"CurrentPP": 10,
					"MaxPP": 10,
					"Priority": 0,
					"Power": 100,
					"Accuracy": 100
				}, {
					"ID": 322,
					"Name": "Cosmic Power",
					"Type": 8192,
					"Category": 0,
					"Targets": 7,
					"CurrentPP": 20,
					"MaxPP": 20,
					"Priority": 0,
					"Power": 0,
					"Accuracy": 0
				}, {
					"ID": 280,
					"Name": "Brick Break",
					"Type": 2,
					"Category": 1,
					"Targets": 10,
					"CurrentPP": 15,
					"MaxPP": 15,
					"Priority": 0,
					"Power": 75,
					"Accuracy": 100
				}],
				"Friendship": 0,
				"OriginalTrainerID": 0,
				"Type": 0
			},
			"Team": 0,
			"Allies": [{
				"Team": 0,
				"Pokemon": {
					"Name": "Mew",
					"NatDex": 151,
					"Level": 6,
					"TotalExperience": 179,
					"Gender": 0,
					"IVs": [3, 1, 1, 4, 0, 3],
					"EVs": [7, 24, 41, 11, 3, 20],
					"Nature": 5,
					"Stats": [28, 17, 17, 17, 17, 17],
					"StatModifiers": [0, 0, 0, 0, 0, 0, 0, 0, 0],
					"StatusEffects": 0,
					"CurrentHP": 26,
					"Moves": [{
						"ID": 447,
						"Name": "Grass Knot",
						"Type": 2048,
						"Category": 2,
						"Targets": 10,
						"CurrentPP": 20,
						"MaxPP": 20,
						"Priority": 0,
						"Power": 0,
						"Accuracy": 100
					}, {
						"ID": 449,
						"Name": "Judgment",
						"Type": 1,
						"Category": 2,
						"Targets": 10,
						"CurrentPP": 10,
						"MaxPP": 10,
						"Priority": 0,
						"Power": 100,
						"Accuracy": 100
					}, {
						"ID": 322,
						"Name": "Cosmic Power",
						"Type": 8192,
						"Category": 0,
						"Targets": 7,
						"CurrentPP": 20,
						"MaxPP": 20,
						"Priority": 0,
						"Power": 0,
						"Accuracy": 0
					}, {
						"ID": 280,
						"Name": "Brick Break",
						"Type": 2,
						"Category": 1,
						"Targets": 10,
						"CurrentPP": 15,
						"MaxPP": 15,
						"Priority": 0,
						"Power": 75,
						"Accuracy": 100
					}],
					"Friendship": 0,
					"OriginalTrainerID": 0,
					"Type": 0
				}
			}],
			"Opponents": [{
				"Team": 1,
				"Party": 1,
				"Slot": 0,
				"Pokemon": {
					"Name": "Absol",
					"NatDex": 359,
					"Level": 60,
					"TotalExperience": 211060,
					"Gender": 0,
					"IVs": [4, 2, 3, 3, 1, 1],
					"EVs": [5, 31, 11, 41, 29, 40],
					"Nature": 2,
					"Stats": [151, 166, 80, 102, 81, 101],
					"StatModifiers": [0, 0, 0, 0, 0, 0, 0, 0, 0],
					"StatusEffects": 0,
					"CurrentHP": 151,
					"Moves": [{
						"ID": 230,
						"Name": "Sweet Scent",
						"Type": 1,
						"Category": 0,
						"Targets": 11,
						"CurrentPP": 20,
						"MaxPP": 20,
						"Priority": 0,
						"Power": 0,
						"Accuracy": 100
					}, {
						"ID": 429,
						"Name": "Mirror Shot",
						"Type": 256,
						"Category": 2,
						"Targets": 10,
						"CurrentPP": 10,
						"MaxPP": 10,
						"Priority": 0,
						"Power": 65,
						"Accuracy": 85
					}, {
						"ID": 284,
						"Name": "Eruption",
						"Type": 512,
						"Category": 2,
						"Targets": 11,
						"CurrentPP": 5,
						"MaxPP": 5,
						"Priority": 0,
						"Power": 150,
						"Accuracy": 100
					}, {
						"ID": 157,
						"Name": "Rock Slide",
						"Type": 32,
						"Category": 1,
						"Targets": 11,
						"CurrentPP": 10,
						"MaxPP": 10,
						"Priority": 0,
						"Power": 75,
						"Accuracy": 90
					}],
					"Friendship": 0,
					"OriginalTrainerID": 0,
					"Type": 0
				}
			}],
			"Targets": [{
				"Team": 0,
				"Party": 0,
				"Slot": 0,
				"Pokemon": {
					"Name": "Mew",
					"NatDex": 151,
					"Level": 6,
					"TotalExperience": 179,
					"Gender": 0,
					"IVs": [3, 1, 1, 4, 0, 3],
					"EVs": [7, 24, 41, 11, 3, 20],
					"Nature": 5,
					"Stats": [28, 17, 17, 17, 17, 17],
					"StatModifiers": [0, 0, 0, 0, 0, 0, 0, 0, 0],
					"StatusEffects": 0,
					"CurrentHP": 26,
					"Moves": [{
						"ID": 447,
						"Name": "Grass Knot",
						"Type": 2048,
						"Category": 2,
						"Targets": 10,
						"CurrentPP": 20,
						"MaxPP": 20,
						"Priority": 0,
						"Power": 0,
						"Accuracy": 100
					}, {
						"ID": 449,
						"Name": "Judgment",
						"Type": 1,
						"Category": 2,
						"Targets": 10,
						"CurrentPP": 10,
						"MaxPP": 10,
						"Priority": 0,
						"Power": 100,
						"Accuracy": 100
					}, {
						"ID": 322,
						"Name": "Cosmic Power",
						"Type": 8192,
						"Category": 0,
						"Targets": 7,
						"CurrentPP": 20,
						"MaxPP": 20,
						"Priority": 0,
						"Power": 0,
						"Accuracy": 0
					}, {
						"ID": 280,
						"Name": "Brick Break",
						"Type": 2,
						"Category": 1,
						"Targets": 10,
						"CurrentPP": 15,
						"MaxPP": 15,
						"Priority": 0,
						"Power": 75,
						"Accuracy": 100
					}],
					"Friendship": 0,
					"OriginalTrainerID": 0,
					"Type": 0
				}
			}, {
				"Team": 1,
				"Party": 1,
				"Slot": 0,
				"Pokemon": {
					"Name": "Absol",
					"NatDex": 359,
					"Level": 60,
					"TotalExperience": 211060,
					"Gender": 0,
					"IVs": [4, 2, 3, 3, 1, 1],
					"EVs": [5, 31, 11, 41, 29, 40],
					"Nature": 2,
					"Stats": [151, 166, 80, 102, 81, 101],
					"StatModifiers": [0, 0, 0, 0, 0, 0, 0, 0, 0],
					"StatusEffects": 0,
					"CurrentHP": 151,
					"Moves": [{
						"ID": 230,
						"Name": "Sweet Scent",
						"Type": 1,
						"Category": 0,
						"Targets": 11,
						"CurrentPP": 20,
						"MaxPP": 20,
						"Priority": 0,
						"Power": 0,
						"Accuracy": 100
					}, {
						"ID": 429,
						"Name": "Mirror Shot",
						"Type": 256,
						"Category": 2,
						"Targets": 10,
						"CurrentPP": 10,
						"MaxPP": 10,
						"Priority": 0,
						"Power": 65,
						"Accuracy": 85
					}, {
						"ID": 284,
						"Name": "Eruption",
						"Type": 512,
						"Category": 2,
						"Targets": 11,
						"CurrentPP": 5,
						"MaxPP": 5,
						"Priority": 0,
						"Power": 150,
						"Accuracy": 100
					}, {
						"ID": 157,
						"Name": "Rock Slide",
						"Type": 32,
						"Category": 1,
						"Targets": 11,
						"CurrentPP": 10,
						"MaxPP": 10,
						"Priority": 0,
						"Power": 75,
						"Accuracy": 90
					}],
					"Friendship": 0,
					"OriginalTrainerID": 0,
					"Type": 0
				}
			}]
		})
	await ctx.send(f"Turn: {type(turn)} {turn.toJSON()}")

@bot.command()
async def start(ctx: commands.Context):
	msg = await ctx.send("Populating battle...")
	async with aiohttp.ClientSession() as session:
		pkmn = []
		for i in range(2):
			async with session.get("http://api:4000/pokedex/generate") as resp:
				pkmn += [await resp.json()]

		start = {
			"Parties": [
				[pkmn[0]],
				[pkmn[1]],
			]
		}
		async with session.post("http://api:4000/battle/new", json=start) as resp:
			logging.debug(f"battle created: {resp.status}")

	bot.loop.create_task(coordinator.battles[0].simulate())
	await msg.edit(content="Battle started.")

@bot.command()
async def qstart(ctx: commands.Context, opponent: str):
	logging.debug("quick starting")
	await challenge(ctx, opponent)
	await start(ctx)

def get_token():
	with open("token", "r") as f:
		return "".join(f.readlines()).strip()

if __name__ == "__main__":
	coordinator.set_bot(bot)
	# reference: https://pgjones.gitlab.io/quart/how_to_guides/event_loop.html
	bot.loop.create_task(serve.app.run_task(host="0.0.0.0", use_reloader=False))
	bot.run(get_token())
