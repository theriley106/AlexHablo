from boto3 import client as botoClient
import json
import os
from googletrans import Translator
lambdas = botoClient("lambda", region_name='us-east-1')
TEXT_TO_SAY = "I was successfully able to modify the Amazon Alexa voice.  Here it is speaking {0} in a {1} accent"
SSML_URL = "https://s3.amazonaws.com/nucilohackathonbucket/{0}"

def checkInFile(region):
	for val in open('/tmp/mp3List.txt').read().split("\n"):
		if region == val:
			return True
	return False

def genSSML(fileName):
	return SSML_URL.format(fileName)

def translateText(text, toLanguage, fromLanguage="en"):
	translator = Translator()
	translation = translator.translate(text, dest=toLanguage)
	return translation.text

def getListOfLanguages(languageList='supportedLanguages.json'):
	return json.load(open("supportedLanguages.json"))

def createmp3List():
	if os.path.exists("/tmp/mp3List.txt") == False:
		os.system("touch /tmp/mp3List.txt")

def returnLanguageAbbrFromFull(fullLanguage):
	for value in getListOfLanguages():
		#value type = dict
		if fullLanguage == value["Full_Name"]:
			#the language that the user
			return value["Abbreviation"].lower()

def generateText(language, accent, languageAbbreviation):
	if languageAbbreviation != "en":
			return translateText(TEXT_TO_SAY.format(language, accent), languageAbbreviation)
	else:
		return TEXT_TO_SAY.format(language, accent)

def genPayload(text, accentAbbreviation):
	return json.dumps({
			  "Text": text,
			  "Region": accentAbbreviation
			})

def returnSSMLResponse(ssmlFile, endSession=True):
	return {
		"version": "1.0",
		"sessionAttributes": {},
		"response": {
			"outputSpeech":
			{
			      "type": "SSML",
			      "ssml": "<speak><audio src='{}'/></speak>".format(SSML_URL.format(ssmlFile))
	    			},
					"shouldEndSession": endSession
				  }
		}

def genAccentSSML(intent):
	try:
		language = intent['slots']['language']['value']
		#Trys to find out if the language is defined
	except:
		language = "English"
		#else defaults as English
	languageAbbreviation = returnLanguageAbbrFromFull(language)
	#Defines the abbreviated version of the language sent in the request
	accent = intent['slots']['accentVal']['value']
	# defines the accent language
	accentAbbreviation = returnLanguageAbbrFromFull(accent)
	# returns accent abbreviation
	text = generateText(language, accent, languageAbbreviation)
	# generate text that gets returned
	print("tell me something in {} in a {} accent".format(language, accent))
	#purely for debug reasons
	lambdas.invoke(FunctionName="ffmpegLambda", InvocationType="RequestResponse", Payload=genPayload(text, accentAbbreviation))
	# This is the lambda function that generates the ssml object
	return returnSSMLResponse("{}.mp3".format(accentAbbreviation))
	# This is the python dict that the echo can interperet

def returnLanguageSlotValue(intent, default="es"):
	try:
		return intent['slots']['language']['value']
	except:
		return default


def on_intent(intent_request, session):
	intent = intent_request["intent"]
	intent_name = intent_request["intent"]["name"]
	if intent_name == 'useAccent':
		return genAccentSSML(intent)
		# This generates the valid response that is sent to the echo

	if intent_name == 'saySomething':
		try:
			languageName = intent['slots']['language']['value'].title()
			region = returnLanguageAbbrFromFull(languageName)
			# this should be a lower case abbreviation: ie. es or en
		except Exception as exp:
			print exp
			region = "es"
		if checkInFile(region) == False:
			f = {
				  "Text": translateText("I was successfully able to modify the Amazon Alexa voice.  Here it is speaking in {}".format(abbr), toLanguage=region),
				  "Region": region
				}
			print("Say Something: {}".format(f))
			lambdas.invoke(FunctionName="ffmpegLambda", InvocationType="RequestResponse", Payload=json.dumps(f))
			# this invokes the lambda function that makes the quote
			with open('/tmp/mp3List.txt', 'a') as file:
				file.write('{}\n'.format(region))
		return {
		"version": "1.0",
		"sessionAttributes": {},
		"response": {
			"outputSpeech":
			{
			      "type": "SSML",
			      "ssml": "<speak><audio src='https://s3.amazonaws.com/nucilohackathonbucket/{}.mp3'/></speak>".format(region)
	    			},
					"shouldEndSession": True
				  }
		}

	elif intent_name == 'aboutDev':
		return alexaHelper.devInfo()
	elif intent_name == "AMAZON.HelpIntent":
		return alexaHelper.get_help_response(REPEATSPEECH)
	elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
		return alexaHelper.handle_session_end_request()

def on_launch(launch_request, session):
	return get_welcome_response()

def get_welcome_response():
	session_attributes = {}
	card_title = "Transit Tracker"
	speech_output = "Modifying Amazon Echo Speech using speech synthesis markup language by Christopher Lambert"
	reprompt_text = "Modifying Amazon Echo Speech using speech synthesis markup language by Christopher Lambert"
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
	output = "Please ask me to generate a scramble.  You can also ask about the Developer of this application.  What can I help you with?"
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
	"text": "Thanks for checking out Rubiks Scrambler!"
		},
		"shouldEndSession": True
	  }
	}

createmp3List()
if __name__ == '__main__':
	on_intent({'intent': {'slots': {'language': {'value': 'Spanish'}}, 'name': 'saySomething'}, 'name': ''}, "")
