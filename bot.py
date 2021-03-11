import asyncio
import json
import aiohttp
import discord
from discord.ext import commands
from discord.message import Message
import serve

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
				results = await resp.json(content_type="text/plain")
				results = json.loads(await resp.read())
				print(f"got {len(results['Transactions'])} transactions")
				await msg.edit(content=f"Round Results: Processed {len(results['Transactions'])}")
			else:
				await msg.edit(f"Simulation failed: got {resp.status} from service")

@bot.command()
async def challenge(ctx: commands.Context, opponent: str):
	msg = await ctx.send(f"{ctx.author} challenging {opponent}")
	if opponent.startswith("<@!") and opponent.endswith(">"):
		pass # TODO: have the user that invoked the command challenge the user @'d here
	else:
		pass

@bot.command()
async def turn(ctx: commands.Context, turn_type: str, turn_arg: str):
	pass

def get_token():
	with open("token", "r") as f:
		return "".join(f.readlines()).strip()

if __name__ == "__main__":
	# reference: https://pgjones.gitlab.io/quart/how_to_guides/event_loop.html
	bot.loop.create_task(serve.app.run_task(host="0.0.0.0", use_reloader=False))
	bot.run(get_token())
