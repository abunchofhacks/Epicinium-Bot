###
# Copyright 2021, A Bunch of Hacks
#
# Made available under the MIT License (see LICENSE.txt)
#
# [authors:]
# Sander in 't Veld (sander@abunchofhacks.coop)
###

import discord
from discord.ext import commands


class DiscordManager(commands.Cog):
	def __init__(self, bot, guild_id):
		self.bot = bot
		self.guild_id = guild_id

	async def assign_playing_role(self, discord_id):
		guild = self.bot.get_guild(self.guild_id)
		playing_role = next(
		    (role for role in guild.roles if role.name == 'playing'), None)
		if playing_role == None:
			return
		member = guild.get_member(discord_id)
		if member == None:
			return
		if playing_role in member.roles:
			return
		await member.add_roles(playing_role)

	async def remove_playing_role(self, discord_id):
		guild = self.bot.get_guild(self.guild_id)
		member = guild.get_member(discord_id)
		if member == None:
			return
		playing_role = next(
		    (role for role in member.roles if role.name == 'playing'), None)
		if playing_role == None:
			return
		await member.remove_roles(playing_role)
