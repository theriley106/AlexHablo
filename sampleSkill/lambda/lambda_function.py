try:
	import echoLinguistics
except:
	raise Exception("You didn't run the config file properly.  Echo linguistics is not in the sample skill directory.")
import alexaHelper

SKILL_NAME = "Echo Linguistics"
# This is also the card title
GREETING_MESSAGE = "Modifying Amazon Echo Speech using speech synthesis markup language by Christopher Lambert"
# This is the message alexa will say when starting the skill
GREETING_MESSAGE2 = "Modifying Amazon Echo Speech using speech synthesis markup language by Christopher Lambert"
# This is the message alexa will say after leaving the skill open for ~10 seconds
TEXT_TO_SAY = "I was successfully able to modify the Amazon Alexa voice.  Here it is speaking {0} in a {1} accent"
# This is the text that the third party voice will say
HELP_RESPONSE = "You can tell me to speak different languages or speak in different accents"
# This is the response that is said when a user asks alexa for help using the skill
END_RESPONSE = "Thank you for checking out Echo Linguistics"
# This is the end request text that is sent when the client exits to skill

def returnLanguageSlotValue(intent, default="Spanish"):
	# This tells the developer the slot values that the client said
	try:
		return intent['slots']['language']['value'].title()
	except:
		# This means that the user didn't fill any language slots in their request
		return default

def on_intent(intent_request, session):
	intent = intent_request["intent"]
	# This is all of the info regarding the intent'
	intent_name = intent_request["intent"]["name"]
	# This is specifically the name of the intent you created

	if intent_name == 'siriVoice':
		return echoLinguistics.speak("I don't think you'd understand a joke in my language  They are not so funny anyway", siri=True)
		# This is the function that says something without modifying accent

	if intent_name == 'useAccent':
		# alexa say something in german with a spanish accent
		languageName = returnLanguageSlotValue(intent, default="English")
		# Full name of the language sent in the request: ie, English, Spanish, etc.
		languageAbbr = echoLinguistics.returnLanguageAbbrFromFull(languageName)
		#Defines the abbreviated version of the language sent in the request
		accentVal = intent['slots']['accentVal']['value']
		# defines the accent language
		accentAbbr = echoLinguistics.returnLanguageAbbrFromFull(accentVal)
		# returns accent abbreviation
		return echoLinguistics.speak(TEXT_TO_SAY.format(languageName, accentVal), accent=accentAbbr, toLanguage=languageAbbr)
		# This is the function that says something without modifying accent

	if intent_name == 'saySomething':
		# example: alexa say something in german
		languageName = returnLanguageSlotValue(intent)
		# Full name of the language sent in the request: ie, English, Spanish, etc.
		languageAbbr = echoLinguistics.returnLanguageAbbrFromFull(languageName)
		# This is the abbreviation of language name: ie, English to en
		return echoLinguistics.speak(TEXT_TO_SAY.format(languageName, languageName), accent=languageAbbr, toLanguage=languageAbbr)
		# This is the function that says something without modifying accent

	elif intent_name == 'aboutDev':
		# Alexa tell me about the developer
		return alexaHelper.devInfo()

	elif intent_name == "AMAZON.HelpIntent":
		# Alexa help
		return alexaHelper.get_help_response(REPEATSPEECH)

	elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
		# Alexa stop / Alexa cancel
		return alexaHelper.handle_session_end_request()

def on_launch(launch_request, session):
	# As soon as the application is loaded
	return get_welcome_response()

def get_welcome_response():
	session_attributes = {}
	card_title = SKILL_NAME
	speech_output = GREETING_MESSAGE
	reprompt_text = GREETING_MESSAGE2
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

def lambda_handler(event, context):
	if event["request"]["type"] == "LaunchRequest":
		return on_launch(event["request"], event["session"])
	elif event["request"]["type"] == "IntentRequest":
		return on_intent(event["request"], event["session"])
	else:
		handle_session_end_request()

def get_help_response():
	output = HELP_RESPONSE
	return returnSpeech(output, False)

def build_speechlet_response(title, output, reprompt_text, should_end_session):
	return {
		"outputSpeech": {
			"type": "PlainText",
			"text": output
		},
		"card": {
			"type": "Simple",
			"title": title,
			"content": output
		},
		"reprompt": {
			"outputSpeech": {
				"type": "PlainText",
				"text": reprompt_text
			}
		},
		"shouldEndSession": should_end_session
	}

def build_response(session_attributes, speechlet_response):
	return {
		"version": "1.0",
		"sessionAttributes": session_attributes,
		"response": speechlet_response
	}

def handle_session_end_request():
	return {
	"version": "1.0",
	"sessionAttributes": {},
	"response": {
	"outputSpeech": {
	"type": "PlainText",
	"text": END_RESPONSE
		},
		"shouldEndSession": True
	  }
	}

