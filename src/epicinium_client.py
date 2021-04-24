###
# Copyright 2021, A Bunch of Hacks
#
# Made available under the MIT License (see LICENSE.txt)
#
# [authors:]
# Sander in 't Veld (sander@abunchofhacks.coop)
###

import json
from typing import cast, Tuple
import logging
import discord
from discord.ext import typed_commands as commands
from discord.ext import tasks
import aiohttp
import asyncio
import struct

from src.tracker import Tracker

log = logging.getLogger(__name__)


class EpiciniumClient(commands.Cog):
	def __init__(self, bot: commands.Bot, config):
		self.bot = bot
		self.web_server: str = config['web-server']
		self.version: str = config['epicinium-version']
		self.account_id: int = config['epicinium-account-id']
		self.session_token: str = config['epicinium-session-token']
		user_agent = "epicinium-bot/{} (python)".format(self.version)
		self.session = aiohttp.ClientSession(
		    loop=self.bot.loop,
		    headers={"User-Agent": user_agent},
		    raise_for_status=True)
		self.writer = None
		self.reader = None
		self.username = None
		self.listen.start()
		log.info("Client started: {}".format(user_agent))

	def cog_unload(self):
		log.info("Client stopped.")

	@tasks.loop(seconds=10)
	async def listen(self):
		host, port = await self.get_server()
		log.info("Connecting to {}:{}...".format(host, port))
		await self.connect(host=host, port=port)
		await self.join()
		await self.keep_listening()
		await self.disconnect()
		log.debug("Connection ended.")

	@listen.after_loop  # type: ignore
	async def on_listen_cancel(self):
		if self.listen.is_being_cancelled():
			if self.writer is not None:
				await self.disconnect()
			await self.session.close()
		return True

	async def get_server(self) -> Tuple[str, int]:
		url = self.web_server + "/api/v1/portal"
		log.info("Accessing portal...")
		result = await self.session.get(url)
		body = await result.json()
		host = body['host']
		port = body['port']
		return host, port

	async def connect(self, *, host: str, port: int):
		log.info("Connecting...")
		reader, writer = await asyncio.open_connection(host, port)
		self.writer = writer
		self.reader = reader
		log.info("Connected.")

	async def join(self):
		message = {
		    'type': 'version',
		    'version': self.version,
		    'metadata': {
		        'patchmode': 'bot'
		    }
		}
		self.writer.write(encode_message(message))
		message = {
		    'type': 'join_server',
		    'sender': self.account_id,
		    'content': self.session_token
		}
		self.writer.write(encode_message(message))
		await self.writer.drain()

	async def keep_listening(self):
		while True:
			message = await self.receive_message()
			if message is None:
				break
			elif message == {}:
				continue
			responses = await self.handle_message(message)
			if responses is None:
				break
			for message in responses:
				self.writer.write(encode_message(message))
			await self.writer.drain()

	async def handle_message(self, message: dict):
		messages = []
		if message['type'] == 'quit':
			log.warning("Received hard quit.")
		elif message['type'] == 'closed':
			log.info("Server is shutting down.")
			return None
		elif message['type'] == 'closing':
			log.info("Server is closing.")
			return None
		elif message['type'] == 'ping':
			# Pings must always be responded with pongs.
			messages = [{'type': 'pong'}]
		elif message['type'] == 'pong':
			pass
		elif message['type'] == 'join_server':
			if 'content' not in message or not message['content']:
				log.error("Failed to join server.")
				return None
			elif self.username is None:
				self.username = message['content']
				log.info("Joined server as '{}'".format(self.username))
			elif message['content'] == self.username:
				pass
			else:
				player_username = message['content']
				tracker = cast(Tracker, self.bot.get_cog('Tracker'))
				await tracker.add_player(player_username)
		elif message['type'] == 'leave_server':
			if 'content' not in message or not message['content']:
				log.error("Failed to join server. (Version mismatch?)")
				return None
			elif self.username is not None and message[
			    'content'] == self.username:
				pass
			else:
				player_username = message['content']
				tracker = cast(Tracker, self.bot.get_cog('Tracker'))
				await tracker.remove_player(player_username)
		elif message['type'] == 'leave_lobby':
			player_username = message['content']
			tracker = cast(Tracker, self.bot.get_cog('Tracker'))
			await tracker.player_left_match(player_username)
		elif message['type'] == 'in_game':
			if 'role' in message and message['role'] == 'observer':
				pass
			else:
				player_username = message['content']
				tracker = cast(Tracker, self.bot.get_cog('Tracker'))
				await tracker.player_started_match(player_username)
		return messages

	async def receive_message(self):
		head: bytes = await self.reader.read(4)
		if len(head) == 0:
			log.error("Unexpected EOF!")
			return None
		elif len(head) < 4:
			log.error("Unexpected EOF with {} trailing bytes!".format(
			    len(head)))
			return None
		messagelen, = struct.unpack('!I', head)
		if messagelen == 0:
			log.debug("Received pulse.")
			return {}
		elif messagelen > 524288:
			log.error(
			    "Refusing to receive message of length {}.".format(messagelen))
			return None
		data = await self.reader.read(messagelen)
		if len(data) < messagelen:
			log.error(
			    "Unexpected EOF while receiving message of length {}!".format(
			        messagelen))
			return None
		jsonstr = data.decode(encoding='ascii')
		log.debug("Received message: {}".format(jsonstr))
		message = json.loads(jsonstr)
		return message

	async def disconnect(self):
		await self.writer.drain()
		log.info("Disconnecting...")
		message = {'type': 'quit'}
		self.writer.write(encode_message(message))
		await self.writer.drain()
		await self.wait_for_closure()
		self.writer.close()
		self.reader = None
		self.writer = None
		log.info("Disconnected.")

	async def wait_for_closure(self):
		while True:
			garbage = await self.reader.read(1024)
			if len(garbage) > 0:
				log.debug("Received {} bytes of garbage.".format(len(garbage)))
			else:
				break


def encode_message(message: dict) -> bytes:
	jsonstr: str = json.dumps(message,
	                          ensure_ascii=True,
	                          separators=(',', ':'))
	log.debug("Sending message: {}".format(jsonstr))
	# Encode the json message in lower ASCII.
	data: bytes = jsonstr.encode(encoding='ascii')
	# Prepend the network order representation of the 32-bit length.
	head: bytes = struct.pack('!I', len(data))
	log.debug("Sending message of length {}".format(len(data)))
	return head + data
