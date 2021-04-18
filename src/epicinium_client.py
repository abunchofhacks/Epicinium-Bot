###

import json
import logging
import discord
from discord.ext import commands, tasks
import aiohttp

log = logging.getLogger(__name__)


class EpiciniumClient(commands.Cog):
	def __init__(self, bot, config):
		self.bot = bot
		self.web_server = config['web-server']
		self.version = config['epicinium-version']
		self.account_id = config['epicinium-account-id']
		self.session_token = config['epicinium-session-token']
		user_agent = "epicinium-bot/{} (python)".format(self.version)
		log.debug("User-Agent: " + user_agent)
		self.session = aiohttp.ClientSession(
		    headers={"User-Agent": user_agent}, raise_for_status=True)
		self.listen.start()
		log.info("Client started.")

	def cog_unload(self):
		log.info("Client stopped.")

	@tasks.loop(seconds=10)
	async def listen(self):
		log.debug("Tick.")
		host, port = await self.get_server()
		log.info("Connecting to {}:{}...".format(host, port))
		# todo
		log.debug("Tock.")

	@listen.after_loop
	async def on_listen_cancel(self):
		if self.listen.is_being_cancelled():
			await self.session.close()

	async def get_server(self):
		url = self.web_server + "/api/v1/portal"
		log.info("Accessing portal...")
		result = await self.session.get(url)
		body = await result.json()
		host = body['host']
		port = body['port']
		return host, port
