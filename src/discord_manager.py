###
# Copyright 2021, A Bunch of Hacks
#
# Made available under the MIT License (see LICENSE.txt)
#
# [authors:]
# Sander in 't Veld (sander@abunchofhacks.coop)
###

import discord
from discord.ext import typed_commands as commands


class DiscordManager(commands.Cog):
	def __init__(self, bot: commands.Bot, guild_id: int):
		self.bot = bot
		self.guild_id = guild_id

	async def assign_playing_role(self, discord_id: int):
		guild = self.bot.get_guild(self.guild_id)
		if guild is None:
			return
		playing_role = next(
		    (role for role in guild.roles if role.name == 'playing'), None)
		if playing_role is None:
			return
		member = guild.get_member(discord_id)
		if member is None:
			return
		if playing_role in member.roles:
			return
		await member.add_roles(playing_role)

	async def remove_playing_role(self, discord_id: int):
		guild = self.bot.get_guild(self.guild_id)
		if guild is None:
			return
		member = guild.get_member(discord_id)
		if member is None:
			return
		playing_role = next(
		    (role for role in member.roles if role.name == 'playing'), None)
		if playing_role is None:
			return
		await member.remove_roles(playing_role)
