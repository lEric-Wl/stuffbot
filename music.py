import discord
from discord.ext import commands
import json
from ytmusicapi import YTMusic
from youtube_dl import YoutubeDL

ytmusic = YTMusic("oauth.json")

class MyView(discord.ui.View):
	def __init__(self, name,link,bot):
		super().__init__()
		self.name = name
		self.bot = bot
		self.link = link
		self.add_button()

	def add_button(self): #To replace te @discord.ui.button decorator to be able to change what the button says
		button = discord.ui.Button(label=self.name, style=discord.ButtonStyle.success)
		button.callback = self.button_callback
		self.add_item(button)

	async def button_callback(self, interaction: discord.Interaction):
		if not await self.bot.is_owner(interaction.user):
			await interaction.response.send_message("No clicking, Dingus!")
			return
			
		await interaction.response.send_message(f'{self.link} {self.name}')

class Music(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		
		self.playing = False
		self.next = []
		
		self.YDL_OPTIONS = {'format': 'bestaudio/best'}
		self.FFMPEG_OPTIONS = {'options': '-vn'}

		self.vc = None
		self.ytdl = YoutubeDL(self.YDL_OPTIONS)

	@discord.slash_command(description="Not working. No touching :)")
	async def play_music(self, ctx, search:str,num_options:int = 3):
		if num_options > 7:
			num_options = 7
			
		if ctx.guild_id != 1152060271788048455 and not await commands.is_owner():
			await ctx.respond('I am still working on this, you Dingus!')
			return
		
		search = ytmusic.search(query=search, filter='songs')
		for i in range(num_options):
			try:
				trackInfo = f"{search[i]['title']}, {search[i]['artists'][0]['name']} {search[i]['videoId']}"
				link = f'https://www.youtube.com/watch?v={search[i]["videoId"]}'
			
			except IndexError:
				break
				
			await ctx.send(view=MyView(trackInfo,link,self.bot))
		await ctx.respond('Choose which song to add to playlist')
			
def setup(bot):
    bot.add_cog(Music(bot))

