import discord
from discord.ext import commands
import deepl
import json

class Translator(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
		
	@commands.Cog.listener()
	async def on_raw_reaction_add(self,payload):
		flags = ['🇺🇸','🇧🇷','🇫🇷','🇷🇴','🇪🇸','🇲🇽','🇨🇳','🇩🇪']
		languages = ['EN-US','PT-BR','FR','RO','ES','ES','ZH','DE']
		lang = ''
		guild = self.bot.get_guild(int(payload.guild_id))
		member = payload.user_id
		channel = guild.get_channel(int(payload.channel_id))
		emoji = payload.emoji.name if payload.emoji.id is None else str(payload.emoji.id)
		ephemeral = False
		
		msg = await channel.fetch_message(payload.message_id)
		last_reaction = msg.reactions[-1]
		users = await last_reaction.users().flatten()
		last_reactor = users[-1]
		
		settingID = f'{guild.id}{member}'

		with open('creds.json','r') as saves:
			creds = json.load(saves)
			saves.close()
		deeplKey = creds['deeplKey']
			
		
		try: 
			save = open('translateSetting.json','r')
			load = json.load(save)
			ephemeral = load[settingID]		
		except (FileNotFoundError):
			with open('translateSetting.json', 'w') as save:
				load = {}
				json.dump(load,save)
		except KeyError:
			pass
			
		settingID = f'{guild.id}{last_reactor.id}'
		for i in range(len(flags)):
			if(emoji == flags[i]):
				lang = languages[i]
				
				translator = deepl.Translator(deeplKey)

				toTranslate = f'Translation:\n\n{str(msg.content)}'
				
				translated = translator.translate_text(toTranslate, target_lang=lang)

				try:
					if(load[settingID] == True):
						introduction = 'Original Message: '
						intro = translator.translate_text(introduction,target_lang = lang)
						wholeMSG = f'{intro} {msg.jump_url}\n\n{translated}'
						await last_reactor.send(wholeMSG)
						await msg.remove_reaction(emoji,last_reactor)
					else:	
						await msg.reply(translated)
				except KeyError:
					await msg.reply(translated)			
				break
			
	@discord.slash_command(description='Setting to private will dm you your translation')
	async def translate_setting(self,ctx, private:discord.Option(bool)):
		await ctx.defer(ephemeral = True)
		
		settingID = f'{ctx.guild.id}{ctx.author.id}'
		if private:
			adj = 'in your DM'
		else:
			adj = 'this server'
			
		
		try:
			with open('translateSetting.json', 'r') as save:
				load = json.load(save)
		except FileNotFoundError:
			with open('translateSetting.json', 'w') as save:
				load = {}

		load[settingID] = private

		with open('translateSetting.json', 'w') as save:
			json.dump(load, save)
		
		await ctx.respond(content = f'Your future translations in this server will be shown in {adj}',ephemeral = True)		
		
	
def setup(bot):
	bot.add_cog(Translator(bot))
