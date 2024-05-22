import discord
from discord.ext import commands

class Rickroll(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
		
	@discord.slash_command()
	async def rickroll(self,ctx,user:discord.Member):
		await ctx.defer()  # Tells Discord the bot will take more than 3 seconds to respond
	
		if(user.id  == 896548243339608114 or user.id == 1167164973227720886):
			await ctx.send(f"{ctx.author.mention} Never gonna give you up, never gonna let you down, never gonna run around, and desert you.")
			print("reverse uno")
		
		else:
			await ctx.send(f"{user.mention} Never gonna give you up, never gonna let you down, never gonna run around, and desert you.")
			print("rickrolled")
		await ctx.respond(file = discord.File("rickroll.gif"))
		
		
def setup(bot):
	bot.add_cog(Rickroll(bot))
