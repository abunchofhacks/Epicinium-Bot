###
# Copyright 2021, A Bunch of Hacks
#
# Made available under the MIT License (see LICENSE.txt)
#
# [authors:]
# Sander in 't Veld (sander@abunchofhacks.coop)
###

import discord
from discord.ext import typed_commands as commands


class DynoPlaceholder(commands.Cog):
	@commands.command()
	async def help(self, ctx):
		pass

	@commands.command()
	async def leaderboard(self, ctx):
		pass

	@commands.command()
	async def wiki(self, ctx):
		pass

	@commands.command()
	async def releasenotes(self, ctx):
		pass

	@commands.command()
	async def website(self, ctx):
		pass

	@commands.command()
	async def privacy(self, ctx):
		pass

	@commands.command()
	async def abunchofhacks(self, ctx):
		pass
