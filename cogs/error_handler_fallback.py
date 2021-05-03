import discord
import traceback
import sys
from discord.ext import commands
import logging, coloredlogs

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=log)


class CommandErrorHandler(commands.Cog):
	"""Handles all errors that occur inside commands. Generally used for invalid command arguments, or handling unexpected errors."""

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
		"""Event that is triggered when an error is raised while invoking a command, and is otherwise not handled by the command's `on_error`.

		:param ctx: The context used for command invocation.
		:param error: The Exception raised.
		"""
		if hasattr(ctx.command, "on_error"):
			log.debug(f"{ctx.command} has an error handler, ignoring this event")
			return

		cog = ctx.cog
		if cog:
			if cog._get_overridden_method(cog.cog_command_error) is not None:
				return

		ignored = (commands.CommandNotFound, )
		error = getattr(error, "original", error)

		if isinstance(error, ignored):
			return

		if isinstance(error, commands.DisabledCommand):
			await ctx.send(f"{ctx.command} has been disabled.")

		elif isinstance(error, commands.NoPrivateMessage):
			try:
				await ctx.author.send(
					f"{ctx.command} can not be used in Private Messages."
				)
			except discord.HTTPException:
				pass

		elif isinstance(error, commands.BadArgument):
			await ctx.send(f"{error}")

		elif isinstance(error, commands.MissingRequiredArgument):
			await ctx.send(f"{error.param} is required, but it was not provided.")

		elif isinstance(error, commands.MaxConcurrencyReached):
			await ctx.send(
				f"{ctx.command} has reached maximum concurrency. Wait for the other calls to complete."
			)

		else:
			log.critical(
				f"Unhandled exception in {ctx.command}:\n{''.join(traceback.format_exception(type(error), error, error.__traceback__))}"
			)
			await ctx.send(
				"Whoops, something really bad happened, but I can't tell you. Check my logs for details."
			)


def setup(bot):
	"""Set up required for `load_extension`."""
	bot.add_cog(CommandErrorHandler(bot))
