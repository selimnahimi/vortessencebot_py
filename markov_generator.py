import collections
import random
import json
import os
import time
import chardet
import sys
import re

# Other PY files
from essentials import *

class Markov:
	'Class for generating Markov Text'

	# Setting basic variables
	def __init__ (self, order):
		self.log = True
		self.order = order
		self.group_size = self.order + 1
		self.text = []
		self.graph = {}
		self.min_length = 2
		self.max_length = 15
		self.fb_token = ""
		self.trained_words = 0
		self.trained_followups = 0
		self.trained_files = 0
		return

	# Training
	def train (self, filename):
		try:
			if getpyversion() == 3:
				with open(filename, 'r', encoding="utf-8") as file_content:
					text = file_content.read()
			elif getpyversion() == 2:
				text = file(filename).read()
		except Exception as e:
			log("Failed to read the following file: " + filename + "\n" + str(e))
			return

		text = re.sub(r'\r\n?|\n', ' ', text)
		text = re.sub(r'  +', ' ', text)

		self.text = text.split( " " )

		self.trained_words += len(self.text)
		self.trained_files += 1

		self.text = self.text + self.text [ : self.order]

		for i in range (0, len (self.text) - self.group_size):
			key = " ".join(self.text [i : i + self.order])
			value = self.text [i + self.order]
			if key in self.graph:
				self.graph [key].append(value)
				self.trained_followups += 1
			else:
				self.graph [key] = [value]
				self.trained_followups += 1
		return

	# Loading json into graph
	def loadjson (self, filename):

		with open(filename) as data_file:
			data = json.load(data_file)

		for key in data:
			if not key in self.graph:
				self.graph [ key ] = []

			for value in data [ key ]:
				self.graph [ key ].append(value)

	# Dump graph into JSON
	def savejson (self):
		if self.log:
			log("Saving JSON")
		with open('./data.json', 'w') as fp:
			json.dump(self.graph, fp)

	# Get all plain text files and train the bot with them
	def collecttext (self, path):
		count = 0
		for dirname, dirnames, filenames in os.walk(path):
			# Print path to all filenames.
			for filename in filenames:
				f = os.path.join(dirname, filename)

				if f.endswith(".txt"):
					count += 1
					self.train(f)

			if '.git' in dirnames:
				# Don't go into any .git directories.
				dirnames.remove('.git')

		if self.log:
			log("Collected " + str(count) + " text files.")


	# Get random image
	#def randomimg (self, path, text=""):
	
	# Generate a sentence
	def generate (self,length=1):
		result = []
		count = 0
		index = 0

		# Get a random key
		keychoice = random.choice ( list ( self.graph ) )

		# TODO: Make so it accepts . ? ! in the middle of the list
		while True:
			#print "Chosen key: " + keychoice
			keychoice = random.choice ( list ( self.graph ) )
			isplit = keychoice.split( " " )[0-self.order]
			if isplit.endswith((".", "?", "!")):
				break

		# Choose a random word and add it to the generated text
		valuechoice = random.choice ( self.graph.get( keychoice ) )
		newkey = " ".join ( keychoice.split ( " " ) [ 1 : ] ) + " " + valuechoice
		generated = newkey + " "

		length = random.randint(self.min_length, self.max_length)
		#log("Initial length: " + str(length))

		# Begin generating
		while True:
			current_list = self.graph.get(newkey)
			if len(generated.split(" ")) > length-1:
				# Text is already too long, check if we can end the sentence
				sentence_enders = []

				for i in range(0,len(current_list)):
					if current_list[i].endswith ( (".", "!", "?") ) and not current_list[i].endswith ( ("Dr.") ):
						sentence_enders.append(current_list[i])

				if not sentence_enders:
					# List is empty
					choice = random.choice(current_list)
				else:
					# List is not empty, can end the sentence
					choice = random.choice(sentence_enders)
			else:
				choice = random.choice(current_list)

			newkey = " ".join(newkey.split ( " " )[1 : ]) + " " + choice
			#print u"NEW KEY '" + newkey + "'"

			generated += " ".join(newkey.split( " " )[-1 : ]) + " "

			if len(generated.split(" ")) > length and newkey.endswith ( (".", "!", "?") ) and not newkey.endswith ( ("Dr.") ):
				break

		#log("Got length: " + str ( len ( generated.split ( " " ) ) ) )

		return generated