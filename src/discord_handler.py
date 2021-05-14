###
# Copyright 2021, A Bunch of Hacks
#
# Made available under the MIT License (see LICENSE.txt)
#
# [authors:]
# Sander in 't Veld (sander@abunchofhacks.coop)
###

from typing import cast
import logging
import discord
from discord.ext import typed_commands as commands
import textwrap
import re

from src.state import State
from src.discord_manager import DiscordManager

log = logging.getLogger(__name__)


class DiscordHandler(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.command()
	async def ping(self, ctx):
		await ctx.send("Pong!")

	@commands.command()
	async def wannaplay(self, ctx, epicinium_username=None):
		state = cast(State, self.bot.get_cog('State'))
		if epicinium_username is None:
			epicinium_username = state.get_username_for_id(ctx.author.id)
		elif is_valid_username(epicinium_username):
			state.update_link(ctx.author.id, epicinium_username)
			state.save_links()
		else:
			epicinium_username = None
		if epicinium_username is None:
			await ctx.message.reply((
			    "Your Discord account is not yet connected"
			    " to an Epicinium username."
			    " Please use `!wannaplay YourUsernameHere`."
			    " (The username is case-sensitive, please enter it correctly.)"
			))
			return
		manager = cast(DiscordManager, self.bot.get_cog('DiscordManager'))
		await manager.assign_lfg_role(ctx.author.id)
		if isinstance(ctx.channel, discord.TextChannel):
			lfg_role = next(
			    (x for x in ctx.author.roles if x.name == 'looking-for-game'),
			    None)
			if lfg_role is not None:
				await ctx.message.add_reaction("\N{Heavy Check Mark}")
				await ctx.send("{} (aka `{}` in-game) is now also {}.".format(
				    ctx.author.display_name, epicinium_username,
				    lfg_role.mention),
				               allowed_mentions=discord.AllowedMentions(
				                   users=False, roles=True))

	@commands.command()
	async def wannaplayoff(self, ctx):
		manager = cast(DiscordManager, self.bot.get_cog('DiscordManager'))
		await manager.remove_lfg_role(ctx.author.id)
		await ctx.message.add_reaction("\N{Heavy Check Mark}")

	@commands.command()
	async def link(self, ctx, discord_user: discord.Member,
	               epicinium_username: str):
		if not await check_author_is_admin(ctx):
			return
		state = cast(State, self.bot.get_cog('State'))
		old_username = state.update_link(discord_user.id, epicinium_username)
		if old_username is not None:
			await ctx.send(
			    "User **{}** was already linked with username `{}`.".format(
			        discord_user.display_name, old_username),
			    allowed_mentions=discord.AllowedMentions.none())
		await ctx.send(
		    "User **{}** is now linked with Epicinium username `{}`.".format(
		        discord_user.display_name, epicinium_username),
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
		state = cast(State, self.bot.get_cog('State'))
		state.remove_link(discord_user.id)
		await ctx.send("User **{}** is now unlinked.".format(
		    discord_user.display_name))
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
		state = cast(State, self.bot.get_cog('State'))
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


def is_valid_username(username: str):
	valid_pattern = re.compile(r"^[a-zA-Z0-9_~.-]{3,36}$")
	return valid_pattern.match(username)
