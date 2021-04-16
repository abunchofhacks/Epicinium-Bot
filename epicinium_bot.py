###

import toml
import discord
from discord.ext.commands import Bot
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import textwrap

discord.VoiceClient.warn_nacl = False

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

bot = Bot(command_prefix='!')

links = {}


@bot.event
async def on_ready():
	log.info("Logged in as {0.user}".format(bot))
	print("Logged in as {0.user}".format(bot))


@bot.command()
async def ping(ctx):
	await ctx.send("Pong!")


@bot.command()
async def listlinks(ctx):
	text = "hugs {} • yes".format(ctx.message.author.mention)
	for chunk in textwrap.wrap(text, width=1500, break_long_words=False):
		await ctx.send(chunk, allowed_mentions=discord.AllowedMentions.none())


bot.run(config['discord-token'])

log.info("Bot stopped.")
