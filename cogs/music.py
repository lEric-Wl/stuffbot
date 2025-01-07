import discord
from discord.ext import commands
import json
from ytmusicapi import YTMusic
import youtube_dl 
import os
#import asyncio

ytmusic = YTMusic("oauth.json")

playlist = []

class MyView(discord.ui.View):
	def __init__(self, name,link,bot,ID,channel):
		super().__init__()
		self.name = name
		self.bot = bot
		self.link = link
		self.add_button()
		self.id = ID
	
		self.playing = False
		self.vc = channel
		self.client = None
		self.connected = False

		self.FFMPEG_OPTIONS = {'options': '-vn'}
		
	def add_button(self): #To replace te @discord.ui.button decorator to be able to change what the button says
		button = discord.ui.Button(label=self.name, style=discord.ButtonStyle.success)
		button.callback = self.button_callback 
		self.add_item(button)

	async def button_callback(self, interaction: discord.Interaction):
		await interaction.response.defer(ephemeral = True)
		global playlist
		
		await interaction.followup.send(f'Loading Music; Should take up to a minute, or longer, depending on duration',ephemeral = True)
		
		try:			
			playlist.append((self.id,self.link))
			self.download()

			await interaction.followup.send(f'Bone apple tea! Happy Music-ing',ephemeral = True)
			print(playlist)
			
			if (not self.playing):
				await self.play(interaction)
			else:
				print('Something is playing')
				return
			
		except TypeError as e:
			await interaction.followup.send(f'Something went wrong, please try again\n{e}',ephemeral = True)
			return
		
		except youtube_dl.utils.DownloadError as e:
			await interaction.followup.send(f'Something went wrong, please try again\n{e}',ephemeral = True)
			return
			
				
	async def play(self, interaction: discord.Interaction):		
		global playlist 

		if len(playlist) > 0:
			
			if (not isinstance(self.vc, discord.voice_client.VoiceClient)):
				try:
					self.client = await self.vc.connect()
					self.connected = True
				except: 
					pass
				
			if (self.client == None and not self.playing):
				self.client = interaction.guild.voice_client
				await self.client.disconnect()
				self.client = await self.vc.connect()
				self.connected = True
				
			print('------------------------------',type(self.client))
	
			track = playlist.pop(0)
			track = track[0]
			
			if(not self.playing and self.connected):
				try:
					self.playing = True
					print('starting track')
					self.client.play(discord.FFmpegPCMAudio(track, **self.FFMPEG_OPTIONS),after = lambda e: self.next(interaction))
				except Exception as e: #Currently, going to the next song doesn't work, and would get stuck in the voice channel. This is a half-assed solution while I work on fixing it
					self.client = interaction.guild.voice_client
					await self.client.disconnect()
					await interaction.followup.send(f'{e} line 87',ephemeral = True)
					self.connected = False
					self.playing = False
			
		else:
			self.playing = False
					

	def next(self,interaction):
		global playlist	
		
		if len(playlist) > 0:	
			self.download()
			print(playlist)
			track = playlist.pop(0)
			track = track[0]
			
			self.client.play(discord.FFmpegPCMAudio(track, **self.FFMPEG_OPTIONS),after = lambda e: self.next(interaction))
		else:
			self.playing = False
			print('No song left')
			return	
		
	def download(self):
		global playlist
		print(playlist)

		options = {
				'format': 'bestaudio/best',
				'extractaudio' : True,  # only keep the audio
				'audioformat' : "mp3",  # convert to mp3 
				'outtmpl': self.id,    # name the file the ID of the video
				'noplaylist' : True,    # only download single song, not playlist
			}
		
		with youtube_dl.YoutubeDL(options) as ydl:
			ydl.cache.remove()
			ydl.download([playlist[0][0]])					
			print('downloaded')

class Music(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.vc = None
	
	#For my bot, it will create a catagory and channel and save it, and use that channel to play the music
	async def load_channel(self,ctx):	
		try:
			with open('music.json','r') as save:
				data = json.load(save)
				self.vc = await self.bot.fetch_channel(data[str(ctx.guild.id)])
		except FileNotFoundError:	
			self.vc = None
		
		print(type(self.vc))
	'''
	Load the music channel id and then search and list the different music options for the buttons
	The parameters for the buttons are:
		Title of the song
		The link to the song
		The discord bot object
		The id of the song
		The id of the voice channels
	'''
	@discord.slash_command(description="EXTREMELY BUGGY AF!!!!!")
	async def play_music(self, ctx, search:str,num_options:int = 3):
		await self.load_channel(ctx)
		
		if self.vc == None:
			await ctx.respond('Make sure the music channel is set up using /setup_music')
			return
			
		if num_options > 7:
			num_options = 7
		
		search = ytmusic.search(query=search, filter='songs')
		for i in range(num_options):
			try:
				title = search[i]['title']
				artist = search[i]['artists'][0]['name']
				
				#Buttons have a max label size of 80 characters. This is to cut off a long title to have it fit within the limitations, also accounting for the other things I'm adding to the final String
				if((len(title) + len(artist)) > 74):
					cutOff = 74-len(artist)
					title = f'{title[:cutOff]}...'
					
				trackInfo = f"{title}, {artist}"
				link = f'https://www.youtube.com/watch?v={search[i]["videoId"]}'
			
			except IndexError:
				break
			
			if isinstance(self.vc, discord.VoiceChannel):
				await ctx.send(view=MyView(trackInfo,
							   link,
							   self.bot,
							   search[i]["videoId"],
							   self.vc))
			else:
				await ctx.respond(type(self.vc))
				return
			print(link)
			
		await ctx.respond('Choose which song to add to playlist')
		
	@discord.slash_command(description = 'Set up the channel for the music bot')
	async def setup_music(self,ctx):
		try:
			with open('music.json','r') as save:
				music_settings = json.load(save)
				save.close()
		except FileNotFoundError:
			music_settings = {}
			
		guild = ctx.guild
		new_cat = await guild.create_category('stuff-bot')
		text = await guild.create_text_channel('music-commands',category = new_cat)
		vc = await guild.create_voice_channel('stuff-player',category = new_cat)
		
		music_settings[guild.id] = vc.id
		self.vc = vc
		
		with open('music.json','w') as save:
			json.dump(music_settings,save)
			save.close()
			
		await ctx.respond('Done',ephemeral = True)	
			
	@discord.slash_command(description = 'Disconnect the music bot in case of error')			
	async def disconnect(self,ctx):
		try:
			client = ctx.guild.voice_client
			await client.disconnect()
		except:
			pass
		await ctx.respond('done',ephemeral = True)

	@discord.slash_command(description = 'Sees the current playlist')
	async def playlist(self,ctx):
		await ctx.respond(playlist)	
	
	@discord.slash_command(description = 'Sees the current playlist')
	async def clear_playlist(self,ctx):
		global playlist
		playlist = []
		await ctx.respond('Playlist Cleared')			
		
def setup(bot):
    bot.add_cog(Music(bot))

