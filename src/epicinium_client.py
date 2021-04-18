###
# Copyright 2021, A Bunch of Hacks
#
# Made available under the MIT License (see LICENSE.txt)
#
# [authors:]
# Sander in 't Veld (sander@abunchofhacks.coop)
###

import json
import logging
import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
import struct

log = logging.getLogger(__name__)


class EpiciniumClient(commands.Cog):
	def __init__(self, bot, config):
		self.bot = bot
		self.web_server = config['web-server']
		self.version = config['epicinium-version']
		self.account_id = config['epicinium-account-id']
		self.session_token = config['epicinium-session-token']
		user_agent = "epicinium-bot/{} (python)".format(self.version)
		self.session = aiohttp.ClientSession(
		    headers={"User-Agent": user_agent}, raise_for_status=True)
		self.listen.start()
		log.info("Client started: {}".format(user_agent))

	def cog_unload(self):
		log.info("Client stopped.")

	@tasks.loop(seconds=10)
	async def listen(self):
		host, port = await self.get_server()
		log.info("Connecting to {}:{}...".format(host, port))
		await self.connect(host=host, port=port)
		log.debug("Connection ended.")

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

	async def connect(self, *, host, port):
		reader, writer = await asyncio.open_connection(host, port)
		message = {
		    'type': 'version',
		    'version': self.version,
		    'metadata': {
		        'patchmode': 'bot'
		    }
		}
		writer.write(encode_message(message))
		message = {
		    'type': 'join_server',
		    'sender': self.account_id,
		    'content': self.session_token
		}
		writer.write(encode_message(message))
		await writer.drain()
		# todo
		writer.close()


def encode_message(message):
	# Encode the json message in lower ASCII.
	data = json.dumps(message, ensure_ascii=True).encode(encoding='ascii')
	# Prepend the network order representation of the 32-bit length.
	head = struct.pack('!I', len(data))
	log.debug("Sending message of length {}".format(len(data)))
	return head + data
