import traceback
import time

# Other PY files
from essentials import *
from facebook_api import Facebook
from markov_generator import Markov

def main():
	markov = Markov   (random.randint(2, 3))
	markov.min_length = 5
	markov.max_length = 20

	fb     = Facebook ( "YOUR_TOKEN" )
	fb.testing = False

	try:
		# Training #
		start_time = time.time()
		markov.collecttext("./markov")
		#markov.collectjsons ("./markov")
		#markov.loadjson("data.json")
		#markov.savejson()
		train_time = time.time() - start_time

		# Text Generation #
		start_time = time.time()
		generated = markov.generate (1)
		generation_time = time.time() - start_time

		if getpyversion() == 2:
			generated = generated.encode('utf8')

		log("GENERATED:")
		log("---------------------------------")
		log(generated)
		log("---------------------------------")
		log("STATS:")
		log("--- Training time: %s seconds ---"   % train_time)
		log("--- Generation time: %s seconds ---" % generation_time)
		log("--- Total training files: %s ---"    % markov.trained_files)
		log("--- Total trained words: %s ---"     % markov.trained_words)
		log("--- Total keys: %s ---"              % len(markov.graph))
		log("--- Total linked words: %s ---"      % markov.trained_followups)

		image = randomimg("./images", generated)
		log("Chosen image: " + str(image))

		# Publishing to Facebook
		if not image:
			image = randomimg("./images")
			log("No tags found, randomly chosen image: " + str(image))
			message_start = "The image was randomly chosen because no tags were found.\n----------\n"
		else:
			log("tags: " + ", ".join(gettags(generated, image)))
			message_start = "The image was chosen because of the following tag(s): " + ", ".join(gettags(generated, image)) + "\n----------\n"

		response = fb.publish_image ( censor(generated), image )

		# Stat comment
		try:
			post_id = response['post_id']

			fb.publish_comment(post_id, str(message_start) + "STATS:\nMarkov order size: " + str(markov.order) + "\nTraining time: " + str(train_time) + " sec\nGeneration time: " + str(generation_time) + " sec\nTotal training files: " + str(markov.trained_files) + "\nTotal trained words: " + str(markov.trained_words) + "\nTotal keys: " + str(len(markov.graph)))
		except Exception:
			log("Response is not valid, ignoring comment\n" + str(response))

		log(response)
	except Exception as e:
		log("Failed to generate sentence. Posting a random image instead.")
		log(traceback.format_exc(e))
		message = "Failed to generate sentence. Posting a random image instead:"

		image = randomimg("./images")
		log("Chosen image: " + str(image))

		if not image:
			response = fb.publish_text ( message )
		else:
			response = fb.publish_image ( message, image )

		log(response)

main()