###

import logging
import discord
from discord.ext import commands
import textwrap

log = logging.getLogger(__name__)


class DiscordHandler(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def ping(self, ctx):
		await ctx.send("Pong!")

	@commands.command()
	async def about(self, ctx):
		await ctx.send("Guild ID: {}".format(ctx.guild.id))

	@commands.command()
	async def link(self, ctx, discord_user: discord.Member,
	               epicinium_username):
		if not await check_author_is_admin(ctx):
			return
		discord_id = str(discord_user.id)
		state = self.bot.get_cog('State')
		old_username = state.update_link(discord_id, epicinium_username)
		if old_username != None:
			await ctx.send(
			    "User {} was already linked with username `{}`.".format(
			        discord_user.mention, old_username),
			    allowed_mentions=discord.AllowedMentions.none())
		await ctx.send(
		    "User {} is now linked with Epicinium username `{}`.".format(
		        discord_user.mention, epicinium_username),
		    allowed_mentions=discord.AllowedMentions.none())
		state.save_links()

	@link.error
	async def link_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send("Please use this command as follows:"
			               " `!link DISCORD_MENTION EPICINIUM_USERNAME`")

	@commands.command()
	async def unlink(self, ctx, discord_user: discord.Member):
		if not await check_author_is_admin(ctx):
			return
		discord_id = str(discord_user.id)
		state = self.bot.get_cog('State')
		state.remove_link(discord_id)
		await ctx.send("User {} is now unlinked.".format(discord_user.mention))
		state.save_links()

	@unlink.error
	async def unlink_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send("Please use this command as follows:"
			               " `!unlink DISCORD_MENTION`")

	@commands.command()
	async def listlinks(self, ctx):
		if not await check_author_is_admin(ctx):
			return
		state = self.bot.get_cog('State')
		textlinks = [
		    "<@{0}> {1}".format(*link) for link in state.links_as_tuples()
		]
		text = " • ".join(textlinks)
		for chunk in textwrap.wrap(text, width=1500, break_long_words=False):
			await ctx.send(chunk,
			               allowed_mentions=discord.AllowedMentions.none())


async def check_author_is_admin(ctx):
	if any(role.name == "admin" for role in ctx.author.roles):
		return True
	else:
		await ctx.send(
		    "{} You are not allowed to perform this command.".format(
		        ctx.author.mention))
		return False