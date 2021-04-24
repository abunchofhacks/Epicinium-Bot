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


class Tracker(commands.Cog):
	def __init__(self):
		self.player_info = {}

	def add_player(self, username: str):
		if not username in self.player_info:
			self.player_info[username] = {
			    'in_game': False,
			}

	def remove_player(self, username: str):
		if username in self.player_info:
			del self.player_info[username]

	def is_player_online(self, username: str) -> bool:
		return username in self.player_info
