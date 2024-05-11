import discord
from discord import Intents
from discord.ext import commands
from enum import Enum, auto
import array
import os
import base64
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import deepl
import json
import requests
import random

botTokens = open('discordBotKeys.json')
tokens = json.loads(botTokens)

discordToken = tokens['discord']
appID = tokens['appID']
vertexProjectId = tokens['vertexID']
vertexEndpoint = tokens['vertexEndpoint']
vertexLocation = "us-central1"
apiEndpoint = "us-central1-aiplatform.googleapis.com"
googleDriveCred = "gspreadCred.json"
sheetID = tokens['sheetID']
deeplKey = tokens['deepl']


intent = discord.Intents.all()
bot = discord.Bot(intents = intent)
translator = deepl.Translator(deeplKey)
'''
class MusicUI(discord.ui.View):
	@discord.ui.button(label="dingus!", style=discord.ButtonStyle.primary, emoji="😎") 
	async def button_callback(self,button,interaction):
		await interaction.response.send_message('Congrats, you\'ve clicked a button')

class SongDropdown(discord.ui.view,options = []):
	@discord.ui.select(placeholder = "Choose a song",min_values = 1, max_values = 1, options = [])
	async def select_callback(self,select,interaction):
		await interaction.response.send_message(select.values[0])
'''		
@bot.event
async def on_ready():
	#await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Stuff"))
	print("Ready\n----------------------------")

@bot.command(description="Sends the bot's latency.") # this decorator makes a slash command
async def ping(ctx): # a slash command will be created with the name "ping"
	await ctx.respond(f"Pong! Latency is {bot.latency}")
	print("recived")

@bot.command(description = "Rickroll someone")
async def rickroll(ctx, user:discord.Member):

	await ctx.defer()  # Tells Discord the bot will take more than 3 seconds to respond
	
	if(user.id  == 896548243339608114 or user.id == 1167164973227720886):
		await ctx.send(f"{ctx.author.mention} Never gonna give you up, never gonna let you down, never gonna run around, and desert you.")
		print("reverse uno")
		
	else:
		await ctx.send(f"{user.mention} Never gonna give you up, never gonna let you down, never gonna run around, and desert you.")
		print("rickrolled")
	await ctx.respond(file = discord.File("rickroll.gif"))
	
@bot.event
async def on_raw_reaction_add(payload):
	flags = ['🇺🇸','🇧🇷','🇫🇷','🇷🇴','🇪🇸','🇲🇽','🇨🇳','🇩🇪']
	languages = ['EN-US','PT-BR','FR','RO','ES','ES','ZH','DE']
	lang = ''
	guild = bot.get_guild(int(payload.guild_id))
	member = payload.user_id
	channel = guild.get_channel(int(payload.channel_id))
	emoji = payload.emoji.name if payload.emoji.id is None else str(payload.emoji.id)
	ephemeral = False
	'''
	settingID = f'{guild.id}{member}'
	try: 
		save = open('translateSetting.json','r')
		load = json.load(save)
		ephemeral = load[settingID]
	except FileNotFoundError:
		pass
	'''	
	for i in range(len(flags)):
		if(emoji == flags[i]):
			lang = languages[i]
			
			msg = await channel.fetch_message(payload.message_id)
			msg_content = msg.content
			
			toTranslate = f'Translation:\n\n{str(msg_content)}'
			translated = translator.translate_text(toTranslate, target_lang=lang)
			
			await msg.reply(translated)
			break
	
@bot.command(description = "Setting for the translator (DOES NOT WORK)")
async def translate_setting(ctx, ephemeral:discord.Option(bool)):
	await ctx.defer(ephemeral = True)
	settingID = f'{ctx.guild.id}{ctx.author.id}'
	adj = '' 
	
	try:
		with open('translateSetting.json', 'r+') as save:
			load = json.load(save)
	except FileNotFoundError:
	    with open('translateSetting.json', 'w') as save:
        	load = {}

	load[settingID] = ephemeral

	with open('translateSetting.json', 'w') as save:
	    json.dump(load, save)
	
	await ctx.respond(content = f'Your future translations in this server will be shown in {adj}',ephemeral = True)			

@bot.event
async def on_message(message):
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

	if message.author.id != 1167164973227720886:
		if load['type'] == 'positive' and load['score'] > 0.5:
			chance = random.randint(0,50)
			if chance > 40:
				await message.reply(': )')
		elif load['type'] == 'negative' and load['score'] < -0.8 and message.author.id != 896548243339608114:
			await message.reply('Dingus!')
		else:
			chance = random.randint(0,50)
			if chance < 3 and message.author.id != 896548243339608114:
				await message.reply('Dingus!')

@bot.command(description = "Not nessacariily insulting")
async def weird_insult(ctx,target:discord.Member,num_adj:int = 3):
	adjs_response = requests.get(f'https://random-word-form.herokuapp.com/random/adjective?count={num_adj}')
	adjs_list = adjs_response.json() 

	if num_adj > 10 and ctx.author.id != 896548243339608114:
		num_adj = 10
	
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
	
@bot.command(description = "Not working")
async def play_music(ctx,search:str,song_options:discord.Option(int)):
	
	if ctx.guild.id != 1152060271788048455:
		await ctx.respond("I'm still working on this and no where close you dingus!")
	
	try:	
		await ctx.defer(ephemeral = True)
	except discord.errors.InteractionResponded:
		return
		
	if song_options > 10:
		song_options = 10
	
	url = 'https://openapi.tidal.com/search'
	headers = {
	    'accept': 'application/vnd.tidal.v1+json',
	    'Authorization': 'Bearer eyJraWQiOiJ2OU1GbFhqWSIsImFsZyI6IkVTMjU2In0.eyJ0eXBlIjoibzJfYWNjZXNzIiwic2NvcGUiOiIiLCJnVmVyIjowLCJzVmVyIjowLCJjaWQiOjEyMjA1LCJleHAiOjE3MTQxODM2MjMsImlzcyI6Imh0dHBzOi8vYXV0aC50aWRhbC5jb20vdjEifQ.qB1VRiQ9dknpPXa0HP_Ll4WE0WDXpHNrXrk-yn9JUCZvkkpspNwT5zf4Eru46pg_F2NkyK23eJXB9hppaAEUOQ',
	    'Content-Type': 'application/vnd.tidal.v1+json'
	}
	params = {
	    'query': search,
	    'offset': '0',
	    'limit': song_options,
	    'countryCode': 'US',
	    'popularity': 'WORLDWIDE'
	}
	all_songs = ['Title       Artist          Album']
	response = requests.get(url, headers=headers, params=params)
	for i in range(0,song_options):
		resource = response.json()['tracks'][i]['resource']
		artist = resource['artists'][0]['name']
		song = resource['title']
		album = resource['album']['title']
		all_songs.append(f'{song}      {artist}     {album}')
		#print(song, artist, album)
	
	for stuff in all_songs:
		print(stuff)
	await ctx.respond('this is a button',view = MusicUI(),ephemeral = True)
	
#@bot.command(description = "LIMITATIONS: May not be 100% accurate. Will NOT account for Crown, Multiple Nobles, Bastard")
async def traitdetect(ctx,image1:discord.Attachment,image2:discord.Attachment = None, image3:discord.Attachment = None, image4:discord.Attachment = None):

	await ctx.defer()
	
	gc = gspread.service_account(filename=googleDriveCred)
	scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
	
	spreadSheetID = sheetID		
	#service = getSheets()
	
	#https://docs.gspread.org/en/latest/user-guide.html#selecting-a-worksheet	

	sheet = gc.open('Edited Noble Trait Calculator')
	wksheet = sheet.sheet1

	#Add all the images to a list, so I can iterate through them
	images = []
	allCoordinates = []
	
	if(image1.content_type.startswith('image')):
		images.append(image1)
	else:
		await ctx.respond(f"{ctx.author.mention}, that's not an image!")
		return
	
	if(image2 is not None): 
		images.append(image2)
	if(image3 is not None): 
		images.append(image3)
	if(image4 is not None): 
		images.append(image4)
	
	#Iterating through all the images
	for image in images:
		
		#The AI cannot accept image links, so I must download them, and delete them after using
		await image.save("image.png")
		#await ctx.send(file= discord.File("image.png"))
		
		if(os.path.getsize("image.png") >= 1450000):
			await ctx.respond("At least one of your image is too big in size. Please crop them")
			os.remove("image.png")
			for stuff in allCoordinates:
				wksheet.update(stuff,False)
			return
			
		try:	
			predictions = predictTraits("image.png")
		except ApplicationCommandInvokeError as e:
			print("File size too large")
		finally:
			print(f"File too large; size = {os.path.getsize('image.png')}") 
			await ctx.respond("At least one of your image is too big in size. Please crop them")
			os.remove("image.png")
			for stuff in allCoordinates:
				wksheet.update(stuff,False)
			return
			
		await ctx.send(f"Found {predictions}")
		traitData = {
					'inbred':'A12','Devoted4':'J8', 
					'Cunning4':'C12','Cunning3':'C13','Cunning2':'C14',
					'Fanatical4':'D12','Fanatical3':'D13','Fanatical2':'D14','Fanatical1':'D15',
					'inspiring4':'E12','inspiring3':'E13','inspiring2':'E14','inspiring1':'E15',					
					'Staunch4':'F12','Staunch3':'F13','Staunch2':'F14','Staunch1':'F15',
					'Tough4':'G12','Tough3':'G13','Tough2':'G14','Tough1':'G15',	
					'Wise4':'H12','Wise3':'H13','Wise2':'H14',
					'martial4':'I12','martial3':'I13','martial2':'I14','martial1':'I15'
					}
		
		for stuff in predictions:
			try:
				coordinate = traitData[stuff]
			except KeyError as e:
				continue
				
			allCoordinates.append(coordinate) #So I can go back and uncheck the boxes
			
			wksheet.update(coordinate,True)
							
		os.remove("image.png")
	
	stats = f"Inf: {wksheet.acell('F18').value} RangedInf: {wksheet.acell('F19').value} Mounted: {wksheet.acell('F20').value} RangedMachine: {wksheet.acell('F21').value} HP: {wksheet.acell('B19').value}"
	
	for stuff in allCoordinates:
		wksheet.update(stuff,False)
		
	await ctx.respond(stats)

def predictTraits( #Copy pasta'd from google's example
	filename = None,
	project = vertexProjectId,
	endpoint_id = vertexEndpoint,
	location = vertexLocation,
	api_endpoint = apiEndpoint):
	
	if(filename == None):
		print("-------------No Image----------------")
		return
	
	# The AI Platform services require regional API endpoints.
	client_options = {"api_endpoint": api_endpoint}
	# Initialize client that will be used to create and send requests.
	# This client only needs to be created once, and can be reused for multiple requests.
	client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
	with open(filename, "rb") as f:
		file_content = f.read()
	print(f"Opened; size = {os.path.getsize('image.png')}")
	# The format of each instance should conform to the deployed model's prediction input schema.
	encoded_content = base64.b64encode(file_content).decode("utf-8")
	instance = predict.instance.ImageObjectDetectionPredictionInstance(content=encoded_content).to_value()
	instances = [instance]
	
	# See gs://google-cloud-aiplatform/schema/predict/params/image_object_detection_1.0.0.yaml for the format of the parameters.
	parameters = predict.params.ImageObjectDetectionPredictionParams(
		confidence_threshold=0.5,
		max_predictions=15,
	).to_value()
	endpoint = client.endpoint_path(
		project=project, location=location, endpoint=endpoint_id
	)
	response = client.predict(
		endpoint=endpoint, instances=instances, parameters=parameters
	)
	# See gs://google-cloud-aiplatform/schema/predict/prediction/image_object_detection_1.0.0.yaml for the format of the predictions.
	predictions = response.predictions
	for prediction in predictions:
		print(" prediction:", prediction['displayNames'])
		
	return prediction['displayNames']
		

		
bot.run(discordToken)
