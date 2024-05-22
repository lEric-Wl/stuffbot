'''	
import discord
from discord.ext import commands
#from enum import Enum, auto
#import array
#import base64
#from google.cloud import aiplatform
#from google.cloud.aiplatform.gapic.schema import predict
#import gspread
#from oauth2client.service_account import ServiceAccountCredentials

#No longer active. Works, but the price to keep it running is too high	

appID = '1167164973227720886'
vertexProjectId = "647197029927" 
vertexEndpoint = "24253027485483008"
vertexLocation = "us-central1"
apiEndpoint = "us-central1-aiplatform.googleapis.com"
googleDriveCred = "gspreadCred.json"
sheetID = '1EtF-vigciamKEHJAPYkBoqtKgwtbxYnDR6mvaxrOnn8'

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
		
'''
