from datetime import datetime
import sys
import ntpath
import os
import random
import re

# Logging into file
dolog = True
def log(x):
	if getpyversion() == 2:
		x = str(x).encode('utf8')

	x = "[" + str(datetime.now())[:-10] + "] " + str(x)
	if dolog:
		file = open('log.txt','a')
		file.write(x + '\n')
		file.close()
	print(x)

# Check if a string is an integer
def isinteger(s):
	try:
		int(s)
		return True
	except ValueError:
		return False

def getpyversion():
	return sys.version_info[0]

def getfilename(path):
	return ntpath.basename(path)

def gettags(text, filename):
	found_tags = []
	tags = getfilename(filename).lower().replace(".jpg","").replace(".png","").split("_")
	text_split = text.lower().split( " " )
	for i in range(0, len(text_split)):
		for j in range(0, len(tags)):
			# Don't count numbers as tags
			if not isinteger(tags[j]):
				word = text_split[i].replace("'s", "").replace("!","").replace("?","").replace(".","").replace(",","")
				if word == tags[j] or word == tags[j] + "s":
					if not tags[j] in found_tags:
						found_tags.append(tags[j])
	return found_tags

def randomimg (path, text=""):
	images = []
	for dirname, dirnames, filenames in os.walk(path):

		# Print path to all filenames.
		for filename in filenames:
			f = os.path.join(dirname, filename)

			# If the file is an image
			if f.lower().endswith( ( ".jpg", ".png" )):
				if not text == "":
					# If there are tags to look for
					tags = getfilename(f).lower().replace(".jpg","").replace(".png","").split("_")
					text_split = text.lower().split(" ")

					for i in range(0, len(text_split)):
						for j in range(0, len(tags)):
							# Don't count numbers as tags
							if not isinteger(tags[j]):
								word = text_split[i].replace("'s", "").replace("!","").replace("?","").replace(".","").replace(",","")
								if word == tags[j] or word == tags[j] + "s":
									images.append(f)
				else:
					# No text, just choose a random image
					images.append(f)

		if '.git' in dirnames:
			# Don't go into any .git directories.
			dirnames.remove('.git')

	if not images:
		return False
	else:
		return random.choice(images)

def repeat_to_length(string_to_expand, length):
	return (string_to_expand * ((length//len(string_to_expand))+1))[:length]

def censor(text):
	censored = text
	bad_words = ['whore','racial','ghetto','nikka','thot','thug','slave','iot','pedo','cancer','shemale','rape','hoe','stupid','dumb','cuck','autist','autism','retard','slut','bitch','jew','gypsy','negro','neger','nigger', 'nigga', 'faggot', 'fag', 'dick', 'vagina', 'pussy', 'cunt', 'cock', 'clit', 'tranny', 'shithead', 'twat', 'dickhead', 'bell-end', 'zipperhead', 'prick']
	for bad_word in bad_words:
		if bad_word.lower() in text.lower():
			insensitive_bad_word_re = re.compile(re.escape(bad_word), re.IGNORECASE)
			censored = insensitive_curse_re.sub(repeat_to_length('@', len(bad_word)), text)
	return censored