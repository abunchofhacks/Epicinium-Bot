###
# Copyright 2021, A Bunch of Hacks
#
# Made available under the MIT License (see LICENSE.txt)
#
# [authors:]
# Sander in 't Veld (sander@abunchofhacks.coop)
###

from typing import List, Tuple, Optional
import json
import discord
from discord.ext import typed_commands as commands
from datetime import datetime


class Link:
	def __init__(self,
	             discord_id: int,
	             epicinium_username: str,
	             discord_id_str: str = None):
		self.discord_id = discord_id
		self.discord_id_str = str(self.discord_id)
		self.epicinium_username = epicinium_username


class State(commands.Cog):
	def __init__(self):
		linkfile = open('saves/latest_links.json', 'r')
		links = json.load(linkfile)['links']
		linkfile.close()
		for link in links:
			if isinstance(link['discord_id'], str):
				link['discord_id'] = int(link['discord_id'])
		self.links = [Link(**link) for link in links]

	def save_links(self):
		savedata = {'links': [link.__dict__ for link in self.links]}
		linkfile = open('saves/latest_links.json', 'w')
		json.dump(savedata, linkfile, indent=2)
		linkfile.close()
		backupfilename = 'saves/{}_links.json'.format(
		    datetime.today().strftime('%Y-%m-%d'))
		linkfile = open(backupfilename, 'w')
		json.dump(savedata, linkfile, indent=2)
		linkfile.close()

	def update_link(self, discord_id: int, epicinium_username: str):
		link = next(
		    (link for link in self.links if link.discord_id == discord_id),
		    None)
		if link is not None:
			old_username = link.epicinium_username
			link.epicinium_username = epicinium_username
			return old_username
		else:
			self.links.append(
			    Link(discord_id=discord_id,
			         epicinium_username=epicinium_username))
			return None

	def remove_link(self, discord_id: int):
		self.links = [
		    link for link in self.links if link.discord_id != discord_id
		]

	def links_as_tuples(self) -> List[Tuple[int, str]]:
		return [(link.discord_id, link.epicinium_username)
		        for link in self.links]

	def get_username_for_id(self, discord_id: int) -> Optional[str]:
		link = next(
		    (link for link in self.links if link.discord_id == discord_id),
		    None)
		if link is not None:
			return link.epicinium_username
		else:
			return None

	def get_id_for_username(self, epicinium_username: str) -> Optional[int]:
		link = next((link for link in self.links
		             if link.epicinium_username == epicinium_username), None)
		if link is not None:
			return link.discord_id
		else:
			return None
