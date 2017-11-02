import discord
import asyncio
from markov_generator import Markov
from essentials import *
import random
import re

generation_responses = ['Give me a second or two...', 'I can feel the power of the vortessence...', 'Hold on...', 'Almost there...', 'Generating sentience...', "Let's see...", 'Sentient or not? That is the question...', "Won't take too long...", 'Galanga...', 'Prepare for Unforeseen Consequences...']

# Class for maintaining the bot on every server
class ServerBot:
	def __init__(self, server):
		self.server = server
		self.order = 3
		self.post_images = True
		self.text_length = 15
		self.channel_blacklist = []
		self.trigger = '>'

		# Privileged options
		self.privileged = True # Enabling this will allow the server to train the bot

		if self.privileged:
			self.p_image_submission_channel = 'None'
			self.p_text_submission_channel = 'None'

server_list = {}

client = discord.Client()

print('Setting up Markov...')
markov_2 = Markov (2)
markov_3 = Markov (3)
markov_2.log = False
markov_3.log = False
print('Training order 2 Markov...')
markov_2.collecttext("./markov")
print('Training order 3 Markov...')
markov_3.collecttext("./markov")

@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')
	print('Getting servers...')
	print('Connected to ' + str(len(list(client.servers))) + ' server(s).')

	for server in list(client.servers):
		server_list[server.id] = ServerBot(server)
		print('Created bot instance for ' + server.id)

@client.event
async def on_message(message):
	# Check if the server is prepared, if not, prepare it
	try:
		bot = server_list[message.server.id]
	except Exception:
		print('Tried accessing unprepared server: ' + message.server.name)
		print('Preparing server now...')
		server_list[message.server.id] = ServerBot(message.server)
		bot = server_list[message.server.id]
		print('Created bot instance for ' + message.server.id)

	message_split = message.content.split(" ")
	#print('Received command (server: ' + str(bot.server.id) + ', sender: ' + str(message.author.id) + '): ' + str(message.content))

	# Bot feed #
	if message.channel.name == "text_submissions":
		if bot.privileged:
			try:
				if len(message.content.split(" ")) < 5:
					await client.add_reaction(message, emoji='❌')
					return

				directory = "./markov/special/feeder/"
				if not os.path.exists(directory):
					os.makedirs(directory)

				text = message.content
				if not text.endswith((".", "?", "!")):
					text = text + "."
				file = open(directory + bot.server.id + '.txt','a')
				file.write(text + '\n')
				file.close()
				await client.add_reaction(message, emoji='✅')
			except Exception as e:
				print('Feeding failed: ' + str(e))
				await client.add_reaction(message, emoji='❌')
	# Commands #

	elif message_split[0] == str(bot.trigger) + 'generate':
		# Text Generator #
		counter = 0
		tmp = await client.send_message(message.channel, '*'+random.choice(generation_responses)+'*')
		if bot.order <= 2:
			generated = markov_2.generate()
		else:
			generated = markov_3.generate()
		#print(generated)

		image = randomimg("./images", generated)

		if not image:
			image = randomimg("./images")
		
		if bot.post_images:
			await client.delete_message(tmp)
			await client.send_file(message.channel, fp=image, content=generated)
		else:
			await client.edit_message(tmp, generated)

	elif message_split[0] == str(bot.trigger) + 'randomimg':
		# Random image #
		image = randomimg("./images")

		if not image:
			await client.send_message(message.channel, '**No images found, sorry.**')
		else:
			fname = " ".join(getfilename(image).lower().replace(".jpg","").replace(".png","").split("_"))
			tags = gettags(fname, image)

			await client.send_file(message.channel, fp=image, content="`Tags: " + ", ".join(tags) + "`")

	elif message_split[0] == str(bot.trigger) + 'order':
		# Set order #
		try:
			if isinteger(message_split[1]):
				if int(message_split[1]) > 1 and int(message_split[1]) < 5:
					bot.order = int(message_split[1])

					await client.send_message(message.channel,'**Order was set to ' + str(bot.order) + '.**')
				else:
					await client.send_message(message.channel, '**The order has to be 2 or 3**')
			else:
				await client.send_message(message.channel, '**The order has to be a number between 2 and 3.**')
		except Exception:
			await client.send_message(message.channel, '*Current order: **' + str(bot.order) + '**\nTo change:* `>order <number between 2-4>`')
	
	elif message_split[0] == str(bot.trigger) + 'reload':
		# Re-train #
		tmp = await client.send_message(message.channel, '**Reloading, this might take a while...**')

		markov_2.graph = {}
		markov_3.graph = {}

		print('Reloading order 2 Markov...')
		markov_2.collecttext("./markov")
		print('Reloading order 3 Markov...')
		markov_3.collecttext("./markov")

		await client.edit_message(tmp, '**Successfully reloaded.**')

	elif message_split[0] == str(bot.trigger) + 'trigger':
		# Send trigger #
		try:
			if len(message_split[1]) > 0 and len(message_split[1]) <= 20:
				if ' ' not in message_split[1]:
					bot.trigger = message_split[1]
					await client.send_message(message.channel, '**The trigger was set to** `' + bot.trigger + '`')
				else:
					await client.send_message(message.channel, '**The trigger cannot contain spaces.**')
			else:
				await client.send_message(message.channel, '**The trigger has to be between 1 and 20 characters long.**')
		except Exception:
			await client.send_message(message.channel, '**The current trigger is:** `' + str(bot.trigger) + '`\n **To change it, do `>trigger [trigger]` **')

	elif message_split[0] == str(bot.trigger) + 'images':
		# Toggle images #
		if bot.post_images:
			bot.post_images = False
			await client.send_message(message.channel, "**The bot won't post images anymore.**")
		else:
			bot.post_images = True
			await client.send_message(message.channel, '**The bot will post images from now on.**')

	'''
	elif message_split[0] == str(bot.trigger) + 'feed':
		# Feed the bot with custom text #
		text = " ".join(message_split[ 1 : ])
		offensive = False

		if bot.privileged:
			for curse in profanity:
				if curse.lower() in text.lower():
					insensitive_curse_re = re.compile(re.escape(curse), re.IGNORECASE)
					text = insensitive_curse_re.sub(repeat_to_length('█', len(curse)), text)
					offensive = True
			if offensive:
				embed = discord.Embed(title=message.author.name, type="rich", author=message.author, colour=discord.Colour.red())
				embed.set_thumbnail(url=message.author.avatar_url)
				embed.add_field(name='Censored Submission:', value=text)
				await client.delete_message(message)
				try:
					await client.send_message(message.channel, embed=embed)
					await client.send_message(message.channel, '**<@'+message.author.id+'> Your submission was modified because offensive/controversial words were found.**')
				except Exception:
					await client.send_message(message.channel, '**<@'+message.author.id+'> Your submission was removed because offensive/controversial words were found and was too long.\nPlease remove the offensive material and re-submit.**')
					return
			if text.endswith((".", "?", "!")):
				try:
					directory = "./markov/feeder/"
					if not os.path.exists(directory):
						os.makedirs(directory)

					file = open(directory + bot.server.id + '.txt','a')
					file.write(text + '\n')
					file.close()
					await client.send_message(message.channel, "*<@"+message.author.id+"> Feeding was successful.*")
				except Exception as e:
					print('Feeding failed: ' + str(e))
					await client.send_message(message.channel, "*<@"+message.author.id+"> Feeding failed.*")
			else:
				await client.send_message(message.channel, "**<@"+message.author.id+"> The text must end with one the following characters: `.` `!` `?` **")
		else:
			await client.send_message(message.channel, "*Sorry, This server doesn't have the privileges to feed the bot.*")
	'''



client.run('YOUR_TOKEN_HERE')