import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='>')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

def main():
    with open("token", "r") as f:
        token = "".join(f.readlines()).strip()
    bot.run(token)
