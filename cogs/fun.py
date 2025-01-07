import discord
from discord.ext import commands
import random
import requests
import json

class Fun(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
	
	rapidApiKey = ''
	@commands.Cog.listener()
	async def on_message(self,message):
		msg = message.content
		url = "https://twinword-sentiment-analysis.p.rapidapi.com/analyze/"
		payload = { "text": msg }
		headers = {
			"content-type": "application/x-www-form-urlencoded",
			"X-RapidAPI-Key": "8edb08ed3cmsh6ca6938d5559d31p1db2d3jsn04e1997c8921",
			"X-RapidAPI-Host": "twinword-sentiment-analysis.p.rapidapi.com"
		}
		
		response = requests.post(url, data=payload, headers=headers)
		load = response.json()
		
		allGifs = [discord.File('kill-you-chuckie.gif'),discord.File('angryMob1.gif'),discord.File('angryVillager.gif'),discord.File('angryVillager2.gif')]
		
		if(('kill' in msg.lower() or 'murder' in msg.lower()) and 'odda' in msg.lower() and message.author.id != 1167164973227720886):
			await message.reply('Kill Odda!', file = random.choice(allGifs))
			
		if('psychologist' in msg.lower()):
			pass
		
		if message.author.id != 1167164973227720886:
			if load['type'] == 'positive' and load['score'] > 0.5:
				chance = random.randint(0,50)
				if chance > 40:
					await message.reply(': )')
			
			elif((message.author.id != 896548243339608114 and message.channel.name != 'council') and (load['type'] == 'negative' and load['score'] < -0.9 or ('dingus' in msg.lower()))):
				await message.reply('Dingus!')

					
def setup(bot):
	bot.add_cog(Fun(bot))
