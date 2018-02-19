from googletrans import Translator


try:
	SECRET_KEY = open("secretKey.txt").read().strip()
	ACCESS_KEY = open("accessKey.txt").read().strip()
	tempBucketID = open("bucketID.txt").read().strip()
except:
	print("No security credentials set up")
	print("create secretCode.txt and accessKey.txt")
	raise Exception("No config files")

# This just confirms that you have all configuration files
FFMPEG_FILE_LOCATION = "/tmp/ffmpeg.linux64"
# /tmp/ is the only lambda folder you have r/w access to
shutil.copyfile('/var/task/ffmpeg.linux64', FFMPEG_FILE_LOCATION)
# This copies the files in /var/task/ffmpeg.linux64 on every lambda run
os.chmod(FFMPEG_FILE_LOCATION, os.stat(FFMPEG_FILE_LOCATION).st_mode | stat.S_IEXEC)
# This makes that ffmpeg file executable
SSML_URL = tempBucketID + "{0}"
# This is the url of the S3 Bucket - make sure this is a publicly available bucket.
DB_FILE = '/tmp/mp3List.txt'
# This is the file where the previously generated file information is stored
LOW_BANDWIDTH = True
# This tells the skill whether or not to regrab duplicate files
LANGUAGE_LIST = json.loads(open("supportedLanguages.json").read())
# This contains all supported languages

def genAccentSSML(intent):
	languageName = returnLanguageSlotValue(intent, default="English")
	# Full name of the language sent in the request: ie, English, Spanish, etc.
	languageAbbreviation = returnLanguageAbbrFromFull(languageName)
	#Defines the abbreviated version of the language sent in the request
	accentVal = intent['slots']['accentVal']['value']
	# defines the accent language
	accentAbbreviation = returnLanguageAbbrFromFull(accentVal)
	# returns accent abbreviation
	text = generateText(languageName, accentVal, languageAbbreviation)
	# generate text that gets returned
	print("tell me something in {} in a {} accent".format(languageName, accentVal))
	#purely for debug reasons
	generateSSML(text, accentAbbreviation)
	# This is the function that generates the ssml audio object
	return returnSSMLResponse("{}.mp3".format(accentAbbreviation))
	# This is the python dict that the echo can interperet

def uploadFile(fileName):
	bucketID = extractBucketID(SSML_URL)
	finalFileName = fileName.split('/')[-1]
	conn = tinys3.Connection(ACCESS_KEY,SECRET_KEY,tls=True)
	conn.upload(finalFileName, open(fileName,'rb'), bucketID)
	return "<speak><audio src='https://s3.amazonaws.com/{}/{}'/></speak>".format(bucketID, fileName)

def editMP3(mp3File):
	# Makes the generated mp3File work on the Echo
	os.system("{} -i {} -ac 2 -codec:a libmp3lame -b:a 48k -ar 16000 -y -vol 1026 /tmp/tmp.mp3 && mv /tmp/tmp.mp3 {}".format(FFMPEG_FILE_LOCATION, mp3File, mp3File))
	#this is the regular FFMPEG command to convert it to a playable audio file.  Notice the tmp and mv tmp.mp3, because -i will overwrite the file as you go along.

def extractBucketID(ssmlValue):
	# This just converts the ssml value into a bucket ID for uploadFile
	return ssmlValue.partition(".com/")[2].partition("/")[0]

def checkInFile(region):
	# This checks to see if the region is in the file exists already
	for val in open(DB_FILE).read().split("\n"):
		# This checks to see if the line in the file matches the region
		if region == val:
			return True
	return False

def generateSSML(text, region=None):
	if region == None:
		region = random.choice(LANGUAGE_LIST)['Abbreviation']
	url = generateURL(text, region.lower())
	mp3File = saveMP3(url, region)
	editMP3(mp3File)
	fileName = uploadFile(mp3File)
	os.system('rm {}'.format(mp3File))
	print("Successfully downloaded")
	return fileName

def saveMP3(mp3URL, region):
	#return MP3 file name
	mp3File = '/tmp/{}.mp3'.format(region)
	#calls it a random file name to later delete
	with open(mp3File, 'wb') as f:
		#this saves the response locally as an actual mp3 file
		f.write(requests.get(mp3URL).content)
	return mp3File

def genSSML(fileName):
	return SSML_URL.format(fileName)

def generateURL(keyWords, region):
	# This generates the GOOGLE TRANSLATE URL
	keyWords = keyWords.replace(" ", "%20")
	# Google translate url doesn't have a space
	return "https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={}&tl={}".format(keyWords, region)

def translateText(text, toLanguage, fromLanguage="en"):
	# This translates text into the language described in fromLanguage
	translator = Translator()
	# Initiates translator class
	translation = translator.translate(text, dest=toLanguage)
	# .to_dict or .text work with this object
	return translation.text