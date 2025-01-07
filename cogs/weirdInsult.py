import discord
from discord.ext import commands
import requests

class WeirdInsult(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
		
	@discord.slash_command()
	async def weird_insult(self,ctx,target:discord.Member,num_adj:int = 3):
	
		if num_adj > 10 and ctx.author.id != 896548243339608114:
			num_adj = 10
		
		adjs_response = requests.get(f'https://random-word-form.herokuapp.com/random/adjective?count={num_adj}')
		adjs_list = adjs_response.json() 

		if isinstance(adjs_list, list):
			if(target.id == 1167164973227720886):
				resp = f'You dare try to insult me? \n\n{ctx.author.mention}, you are a '			
			else:
				resp = f'A weird insult from {ctx.author.mention} <3 \n\n{target.mention}, you are a '
			for adj in adjs_list:
			    resp += adj + ' '
			
		noun = requests.get(f'https://random-word-form.herokuapp.com/random/noun?count=1')
		if target.id == 995051165614096505:
			resp += 'psychologist'	
		elif target.id == 1167164973227720886:
			resp += 'dingus!'	
		else:
			resp += noun.json()[0]
			
		await ctx.respond(resp)
		
def setup(bot):
	bot.add_cog(WeirdInsult(bot))
