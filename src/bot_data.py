###
# Copyright 2021, A Bunch of Hacks
#
# Made available under the MIT License (see LICENSE.txt)
#
# [authors:]
# Sander in 't Veld (sander@abunchofhacks.coop)
###

import json
from typing import cast
import logging
import discord
from discord.ext import typed_commands as commands

from src.state import State

log = logging.getLogger(__name__)


class BotData(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	async def handle(self, message_content: str):
		data = json.loads(message_content)
		if data['type'] == 'link':
			discord_id = data['discord_id']
			epicinium_username = data['username']
			await self.handle_link(discord_id, epicinium_username)
		elif data['type'] == 'game_started':
			pass
		elif data['type'] == 'game_ended':
			pass
		else:
			log.debug("Ignoring bot data of type: {}".format(data['type']))

	async def handle_link(self, discord_id: int, epicinium_username: str):
		state = cast(State, self.bot.get_cog('State'))
		state.update_link(discord_id, epicinium_username)
		state.save_links()
