###
# Copyright 2021, A Bunch of Hacks
#
# Made available under the MIT License (see LICENSE.txt)
#
# [authors:]
# Sander in 't Veld (sander@abunchofhacks.coop)
###

from typing import cast, Dict
import discord
from discord.ext import typed_commands as commands

from src.state import State
from src.discord_manager import DiscordManager


class Info:
	def __init__(self, discord_id: int):
		self.discord_id = discord_id
		self.is_in_game: bool = False


class Tracker(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.player_info: Dict[str, Info] = {}

	async def add_player(self, username: str):
		if username in self.player_info:
			return
		state = cast(State, self.bot.get_cog('State'))
		discord_id = state.get_id_for_username(username)
		if discord_id is None:
			return
		self.player_info[username] = Info(discord_id)
		manager = cast(DiscordManager, self.bot.get_cog('DiscordManager'))
		await manager.assign_playing_role(discord_id)

	async def remove_player(self, username: str):
		if username not in self.player_info:
			return
		discord_id = self.player_info[username].discord_id
		del self.player_info[username]
		manager = cast(DiscordManager, self.bot.get_cog('DiscordManager'))
		await manager.remove_playing_role(discord_id)

	async def player_started_match(self, username: str):
		info = self.player_info.get(username)
		if info is None:
			return
		info.is_in_game = True
		manager = cast(DiscordManager, self.bot.get_cog('DiscordManager'))
		await manager.suppress_lfg_role(info.discord_id)

	async def player_left_match(self, username: str):
		info = self.player_info.get(username)
		if info is None:
			return
		info.is_in_game = False
		manager = cast(DiscordManager, self.bot.get_cog('DiscordManager'))
		await manager.restore_lfg_role(info.discord_id)

	def is_player_online(self, username: str) -> bool:
		return username in self.player_info
