## api_key
## api_secret

# start of code
import flickrapi
import json
from datetime import datetime
import cProfile

flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')

textOptions = ["sky", "clouds", "sun", "stars"]
cityList = {"San Francisco": {"lat": 37.7882, "lon": -122.416}}

def idsToURL(photoId, secretId, server, size):
	return "https://farm9.staticflickr.com/" + str(server) + "/" + str(photoId) + "_" + str(secretId) + "_" + size + ".jpg"

def extractURL(photoData):
	return idsToURL(photoData['id'], photoData['secret'], photoData['server'], "m")

def timeToRoundHour(time):
	if time == '00:00:00':
		return 'na'
	elif int(time.split(":")[1]) < 30:
		return int(time.split(":")[0])
	else:
		return (int(time.split(":")[0]) + 1) % 24

def getPhotoInfo(photoData):
	photoId = photoData['id']
	myData = {'URL': extractURL(photoData), 'photoId': photoId}

	info = flickr.photos.getInfo(photo_id=photoId)['photo']

	# note - currently failing to add one to day of year if between 23:30 and rounding to 0
	takenDate = info['dates']['taken'].split(" ")
	
	myData["takenDayOfYear"] = datetime.strptime(takenDate[0], '%Y-%m-%d').timetuple().tm_yday
	myData["takenHour"] = timeToRoundHour(takenDate[1])
	myData['usagePermissions'] = info['usage']
	myData['publicVis'] = info['visibility']['ispublic']
	
	return myData

def createHourDayObject(inputPhotoData):
	hourDaySet = [[[] for y in range(24)] for x in range(366)]
	for i in inputPhotoData:
		k = getPhotoInfo(i)
		if k['takenDayOfYear'] != 'na' and k['takenHour'] != 'na':
			hourDaySet[int(k['takenDayOfYear'])][int(k['takenHour'])].append({'URL': k['URL']})
	return hourDaySet


def getFlickrData(searchText, city, cities):
	k = []
	# note - this just gets page 1 - 3, increase range value to get more pages (note - might be quite slow)
	for i in range(3):
		k.extend(flickr.photos.search(text=searchText, lat=cities[city]['lat'], lon= cities[city]['lon'], page = i)['photos']['photo'])
	return k

skySF = getFlickrData('sky', 'San Francisco', cityList)
print(skySF)

outputData = createHourDayObject(skySF)

with open('output.txt', 'w') as outfile:
    json.dump(outputData, outfile)
