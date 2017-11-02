import requests
import traceback

# Other PY files
from essentials import *

class Facebook:
	'Class for using the Facebook API'

	def __init__ (self, key):
		self.token = key
		self.url = "https://graph.facebook.com/"
		self.testing = False
		return

	def publish_text(self, message):
		if self.testing:
			return "TESTING"
		else:
			return requests.post(str(self.url) + "me/feed", data=dict(access_token=self.token, message=message)).json()

	def publish_image(self, message, image):
		if self.testing:
			return "TESTING"
		else:
			try:
				files = {'file': open(image ,'rb')}
				return requests.post(str(self.url) + "me/photos", data=dict(access_token=self.token, message=message), files=files).json()
			except Exception as e:
				log("Failed to load the following image: " + str(image) + ", posting text only instead")
				log(traceback.format_exc(e))

				return self.publish_text(text)

	def publish_comment(self, id, message):
		if self.testing:
			return "TESTING"
		else:
			return requests.post(self.url + str(id) + "/comments", data=dict(access_token=self.token, message=message))