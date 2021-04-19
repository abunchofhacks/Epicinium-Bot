###
# Copyright 2021, A Bunch of Hacks
#
# Made available under the MIT License (see LICENSE.txt)
#
# [authors:]
# Sander in 't Veld (sander@abunchofhacks.coop)
###

import json
import discord
from discord.ext import commands
from datetime import datetime


class State(commands.Cog):
	def __init__(self):
		linkfile = open('saves/latest_links.json', 'r')
		self.links = json.load(linkfile)['links']
		linkfile.close()

	def save_links(self):
		linkfile = open('saves/latest_links.json', 'w')
		json.dump({'links': self.links}, linkfile, indent=2)
		linkfile.close()
		backupfilename = 'saves/{}_links.json'.format(
		    datetime.today().strftime('%Y-%m-%d'))
		linkfile = open(backupfilename, 'w')
		json.dump({'links': self.links}, linkfile, indent=2)
		linkfile.close()

	def update_link(self, discord_id, epicinium_username):
		link = next(
		    (link for link in self.links if link['discord_id'] == discord_id),
		    None)
		if link != None:
			old_username = link['epicinium_username']
			link['epicinium_username'] = epicinium_username
			return old_username
		else:
			self.links.append({
			    'discord_id': discord_id,
			    'epicinium_username': epicinium_username
			})
			return None

	def remove_link(self, discord_id):
		self.links = [
		    link for link in self.links if link['discord_id'] != discord_id
		]

	def links_as_tuples(self):
		return [(link['discord_id'], link['epicinium_username'])
		        for link in self.links]

	def get_username_for_id(self, discord_id):
		link = next(
		    (link for link in self.links if link['discord_id'] == discord_id),
		    None)
		if link != None:
			return link['epicinium_username']
		else:
			return None
