###
# Copyright 2021, A Bunch of Hacks
#
# Made available under the MIT License (see LICENSE.txt)
#
# [authors:]
# Sander in 't Veld (sander@abunchofhacks.coop)
###

from typing import Dict
from datetime import datetime, timedelta
import discord
from discord.ext import typed_commands as commands
from discord.ext import tasks


class DiscordManager(commands.Cog):
	def __init__(self, bot: commands.Bot, guild_id: int):
		self.bot = bot
		self.guild_id = guild_id
		self.last_lfg_time: Dict[int, datetime] = {}
		self.remove_afk_from_lfg.start()

	@tasks.loop(seconds=600)
	async def remove_afk_from_lfg(self):
		guild = self.bot.get_guild(self.guild_id)
		if guild is None:
			return
		lfg_role = next(
		    (role for role in guild.roles if role.name == 'looking-for-game'),
		    None)
		if lfg_role is None:
			return
		# Remove lfg from members that are not currently online in Epicinium
		# and have not played or reconfirmed their lfg-ness for a while.
		timeout = timedelta(hours=2)
		for member in lfg_role.members:
			if self.last_lfg_time.get(member.id) is None:
				self.last_lfg_time[member.id] = datetime.now()
			elif any(role.name == 'playing' for role in member.roles):
				self.last_lfg_time[member.id] = datetime.now()
			elif self.last_lfg_time[member.id] + timeout < datetime.now():
				await member.remove_roles(lfg_role)

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

	async def assign_lfg_role(self, discord_id: int):
		guild = self.bot.get_guild(self.guild_id)
		if guild is None:
			return
		lfg_role = next(
		    (role for role in guild.roles if role.name == 'looking-for-game'),
		    None)
		if lfg_role is None:
			return
		member = guild.get_member(discord_id)
		if member is None:
			return
		self.last_lfg_time[member.id] = datetime.now()
		if lfg_role in member.roles:
			return
		await member.add_roles(lfg_role)
		suppression_role = next(
		    (role for role in member.roles
		     if role.name == 'looking-for-game-but-playing'), None)
		if suppression_role is None:
			return
		await member.remove_roles(suppression_role)

	async def remove_lfg_role(self, discord_id: int):
		guild = self.bot.get_guild(self.guild_id)
		if guild is None:
			return
		member = guild.get_member(discord_id)
		if member is None:
			return
		lfg_roles = [
		    role for role in member.roles if role.name == 'looking-for-game'
		    or role.name == 'looking-for-game-but-playing'
		]
		if not lfg_roles:
			return
		await member.remove_roles(*lfg_roles)

	async def suppress_lfg_role(self, discord_id: int):
		guild = self.bot.get_guild(self.guild_id)
		if guild is None:
			return
		member = guild.get_member(discord_id)
		if member is None:
			return
		lfg_role = next(
		    (role for role in member.roles if role.name == 'looking-for-game'),
		    None)
		if lfg_role is None:
			return
		await member.remove_roles(lfg_role)
		suppression_role = next(
		    (role for role in guild.roles
		     if role.name == 'looking-for-game-but-playing'), None)
		if suppression_role is None:
			return
		await member.add_roles(suppression_role)

	async def restore_lfg_role(self, discord_id: int):
		guild = self.bot.get_guild(self.guild_id)
		if guild is None:
			return
		member = guild.get_member(discord_id)
		if member is None:
			return
		suppression_role = next(
		    (role for role in member.roles
		     if role.name == 'looking-for-game-but-playing'), None)
		if suppression_role is None:
			return
		await member.remove_roles(suppression_role)
		lfg_role = next(
		    (role for role in guild.roles if role.name == 'looking-for-game'),
		    None)
		if lfg_role is None:
			return
		await member.add_roles(lfg_role)
		self.last_lfg_time[member.id] = datetime.now()
