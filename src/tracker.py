###
# Copyright 2021, A Bunch of Hacks
#
# Made available under the MIT License (see LICENSE.txt)
#
# [authors:]
# Sander in 't Veld (sander@abunchofhacks.coop)
###

from typing import cast, Dict, Optional
import discord
from discord.ext import typed_commands as commands
from discord.ext import tasks

from src.state import State
from src.discord_manager import DiscordManager


class Info:
	def __init__(self, discord_id: int):
		self.discord_id = discord_id
		self.is_in_game: bool = False


class Tracker(commands.Cog):
	def __init__(self, bot: commands.Bot, online_count_channel_id: int = None):
		self.bot = bot
		self.player_info: Dict[str, Info] = {}
		self.last_updated_online_count: Optional[int] = None
		if online_count_channel_id is not None:
			self.online_count_channel_id: int = online_count_channel_id
			self.update_online_count.start()

	@tasks.loop(seconds=3)
	async def update_online_count(self):
		current_count = len(self.player_info)
		if self.last_updated_online_count is not None:
			if self.last_updated_online_count == current_count:
				return
		channel = self.bot.get_channel(self.online_count_channel_id)
		if channel is None:
			return
		if not isinstance(channel, discord.TextChannel):
			return
		if channel.topic is None:
			return
		parts = channel.topic.split(' | ', 1)
		if len(parts) == 2:
			rest_of_topic = parts[1]
		else:
			rest_of_topic = channel.topic
		new_topic = "Online: {} | {}".format(current_count, rest_of_topic)
		await channel.edit(topic=new_topic)
		self.last_updated_online_count = current_count

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
