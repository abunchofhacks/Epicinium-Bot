###

import toml
import json
import discord
import discord.ext.commands as commands
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import textwrap
from datetime import datetime
import traceback

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

bot = commands.Bot(command_prefix='!', help_command=None)

linkfile = open('saves/latest_links.json', 'r')
links = json.load(linkfile)['links']
linkfile.close()


async def save_links():
	linkfile = open('saves/latest_links.json', 'w')
	json.dump({'links': links}, linkfile, indent=2)
	linkfile.close()
	backupfilename = 'saves/{}_links.json'.format(
	    datetime.today().strftime('%Y-%m-%d'))
	linkfile = open(backupfilename, 'w')
	json.dump({'links': links}, linkfile, indent=2)
	linkfile.close()


@bot.event
async def on_ready():
	log.info("Logged in as {0.user}".format(bot))
	print("Logged in as {0.user}".format(bot))


@bot.event
async def on_error(event, *args, **kwargs):
	log.error(traceback.format_exc())


@bot.event
async def on_command_error(ctx, error):
	log.error(error)


@bot.command()
async def ping(ctx):
	await ctx.send("Pong!")


@bot.command()
async def link(ctx, discord_user: discord.Member, epicinium_username):
	discord_id = str(discord_user.id)
	link = next((link for link in links if link['discord_id'] == discord_id),
	            None)
	if link != None:
		await ctx.send("User {} was already linked with username `{}`.".format(
		    discord_user.mention, link['epicinium_username']))
		link['epicinium_username'] = epicinium_username
	else:
		links.append({
		    'discord_id': discord_id,
		    'epicinium_username': epicinium_username
		})
	await ctx.send(
	    "User {} is now linked with Epicinium username `{}`.".format(
	        discord_user.mention, epicinium_username))
	await save_links()


@link.error
async def link_error(ctx, error):
	if isinstance(error, commands.BadArgument):
		await ctx.send("Please use this command as follows:"
		               " `!link DISCORD_MENTION EPICINIUM_USERNAME`")


@bot.command()
async def listlinks(ctx):
	textlinks = [
	    "<@{}> {}".format(link['discord_id'], link['epicinium_username'])
	    for link in links
	]
	text = " • ".join(textlinks)
	for chunk in textwrap.wrap(text, width=1500, break_long_words=False):
		await ctx.send(chunk, allowed_mentions=discord.AllowedMentions.none())


@bot.command()
async def help(ctx):
	pass


@bot.command()
async def leaderboard(ctx):
	pass


@bot.command()
async def wiki(ctx):
	pass


@bot.command()
async def releasenotes(ctx):
	pass


@bot.command()
async def website(ctx):
	pass


@bot.command()
async def privacy(ctx):
	pass


@bot.command()
async def abunchofhacks(ctx):
	pass


bot.run(config['discord-token'])

log.info("Bot stopped.")
