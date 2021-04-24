###
# Copyright 2021, A Bunch of Hacks
#
# Made available under the MIT License (see LICENSE.txt)
#
# [authors:]
# Sander in 't Veld (sander@abunchofhacks.coop)
###

import toml
import discord
from discord.ext import typed_commands as commands
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import cast

from src.state import State
from src.tracker import Tracker
from src.bot_data import BotData
from src.discord_manager import DiscordManager
from src.discord_handler import DiscordHandler
from src.dyno_placeholder import DynoPlaceholder
from src.epicinium_client import EpiciniumClient

discord.VoiceClient.warn_nacl = False

config = toml.load('config.toml')

Path('logs').mkdir(parents=True, exist_ok=True)

handler = RotatingFileHandler('logs/epicinium_bot.log',
                              encoding='utf-8',
                              maxBytes=1000000,
                              backupCount=100)
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

log_levels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}
log_level = log_levels[config['log-level']]

logging.getLogger('discord').setLevel(log_levels[config['log-level-discord']])
logging.getLogger('discord').addHandler(handler)

log = logging.getLogger(__name__)
log.setLevel(log_level)
log.addHandler(handler)

logging.getLogger('src.bot_data').setLevel(log_level)
logging.getLogger('src.bot_data').addHandler(handler)

logging.getLogger('src.discord_handler').setLevel(log_level)
logging.getLogger('src.discord_handler').addHandler(handler)

logging.getLogger('src.epicinium_client').setLevel(log_level)
logging.getLogger('src.epicinium_client').addHandler(handler)

epicinium_application_id = config['application-id']
guild_id = config['guild-id']
listen_to_dm = config['listen-to-dm']

intents = discord.Intents.default()
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)
bot.add_cog(State())
bot.add_cog(Tracker())
bot.add_cog(DiscordManager(bot, guild_id))
bot.add_cog(BotData(bot))
bot.add_cog(DynoPlaceholder())
bot.add_cog(DiscordHandler(bot))
bot.add_cog(EpiciniumClient(bot, config))


@bot.event
async def on_ready():
	log.info("Logged in as {0.user}".format(bot))
	print("Logged in as {0.user}".format(bot))


@bot.event
async def on_command_error(ctx, error):
	log.error(error)


@bot.event
async def on_member_update(before, after):
	global guild_id
	if after.guild.id != guild_id:
		return
	elif (after.activity is not None
	      and after.activity.type == discord.ActivityType.playing
	      and not isinstance(after.activity, discord.Game)
	      and not isinstance(after.activity, discord.Streaming)
	      and after.activity.application_id == epicinium_application_id):
		manager = bot.get_cog('DiscordManager')
		await manager.assign_playing_role(after.id)
	else:
		state = cast(State, bot.get_cog('State'))
		tracker = cast(Tracker, bot.get_cog('Tracker'))
		username = state.get_username_for_id(after.id)
		if username is not None and tracker.is_player_online(username):
			pass
		else:
			manager = cast(DiscordManager, bot.get_cog('DiscordManager'))
			await manager.remove_playing_role(after.id)


@bot.event
async def on_message(message):
	global guild_id
	if message.author == bot.user:
		return
	elif isinstance(message.channel, discord.DMChannel):
		if listen_to_dm:
			await bot.process_commands(message)
		else:
			return
	elif message.guild.id != guild_id:
		return
	elif (isinstance(message.channel, discord.TextChannel)
	      and message.channel.name == 'bot-data'
	      and message.content.startswith('{')
	      and message.content.endswith('}')):
		bot_data = cast(BotData, bot.get_cog('BotData'))
		await bot_data.handle(message.content)
	else:
		await bot.process_commands(message)


log.info("Bot started.")

bot.run(config['discord-token'])

log.info("Bot stopped.")
