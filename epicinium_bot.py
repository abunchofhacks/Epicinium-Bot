###

import toml
import discord
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

config = toml.load('config.toml')

Path('logs').mkdir(parents=True, exist_ok=True)

handler = RotatingFileHandler('logs/epicinium_bot.log',
                              encoding='utf-8',
                              maxBytes=1000000,
                              backupCount=100)
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

loglevels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}

logging.getLogger('discord').setLevel(loglevels.get(config['log-level']))
logging.getLogger('discord').addHandler(handler)

log = logging.getLogger(__name__)
log.setLevel(loglevels.get(config['log-level']))
log.addHandler(handler)

log.info("Bot started.")

client = discord.Client()


@client.event
async def on_ready():
	print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if message.content.startswith('$hello'):
		await message.channel.send("Hello!")


client.run(config['discord-token'])

log.info("Bot stopped.")
