import requests
import settings
import json
import time

class Weather:
        def __init__(self):
                self.nextupdate = -1
                self.lasttemp = None

        def getCurrentWeather(self):
                currentWeatherURL = "http://api.openweathermap.org/data/2.5/weather"
                PARAMS = { 'appid':settings.api_key, 'q':'berkley' }
                if self.nextupdate < time.time():
                        print("Updating Weather information from API")
               	        r = requests.get(url = currentWeatherURL, params = PARAMS) 
                        jsonData = json.loads(r.text)
                        jsonMain = jsonData["main"]
                        jsonTempK = jsonMain["temp"]
                        self.lasttemp = json.dumps(jsonTempK)
                        self.nextupdate = int(time.time()) 
                        self.nextupdate = self.nextupdate + (60 * 10)
                        print("Next API Update",self.nextupdate)
                return self.lasttemp
