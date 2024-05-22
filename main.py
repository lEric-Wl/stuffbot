import discord
from discord import Intents
from discord.ext import commands
import requests
import random
import json

with open('creds.json','r') as saves:
		creds = json.load(saves)
		saves.close()
deeplKey = creds['discordKey']

intent = discord.Intents.all()
bot = discord.Bot(intents = intent)
allCogs = ['rickroll','weirdInsult','translator','fun','music']

@bot.event
async def on_ready():
	print("Ready\n----------------------------")
	
@bot.command(description = 'Not for you to use')
async def reload(ctx, extension = None):
	
	if not await bot.is_owner(ctx.author):
		await ctx.respond('I told you in the description this is not for you to use, you Dingus!')
		return
	if extension is not None:
		try:	
			bot.reload_extension(f"cogs.{extension}")
		except discord.ExtensionError as e:	
			await ctx.respond(e,ephemeral = True)
			return
	else:
		for stuff in allCogs:
			try:
				bot.reload_extension(f'cogs.{stuff}')	
			except:
				pass
		
	print("reloaded")
	await ctx.respond('Done',ephemeral = True)

  
@bot.command()
async def ping(ctx):
	await ctx.respond(f"Pong! Latency is {bot.latency}")
	print("recived")

for stuff in allCogs:
	bot.load_extension(f'cogs.{stuff}')	
	
bot.run(discordToken)



