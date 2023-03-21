import requests
import settings
import json
import time

class Weather:
        def __init__(self):
                self.nextupdate = -1
                self.lasttemp = None
                self.lastforecast = None
                self.forecastupdate = -1

        def getCurrentWeather(self):
                currentWeatherURL = "http://api.openweathermap.org/data/2.5/weather"
                PARAMS = { 'appid':settings.api_key, 'q': settings.city }
                if self.nextupdate < time.time():
                        print("Updating Weather information from API")
                        r = requests.get(url = currentWeatherURL, params = PARAMS) 
                        jsonData = json.loads(r.text)
                        jsonMain = jsonData["main"]
                        jsonTempK = jsonMain["temp"]

                        if not 'rain' in jsonData or len(jsonData['rain']) == 0:
                                print("No Rain Precip detected")
                        else:
                                jsonRain = jsonData["rain"]
                                self.rain3h = jsonRain["1h"]

                        if not 'snow' in jsonData or len(jsonData['snow']) == 0:
                                print("No Snow Precip detected")
                        else:
                                jsonSnow = jsonData["snow"]
                                self.snow1h = jsonSnow["1h"]

                        self.lasttemp = json.dumps(jsonTempK)
                        self.nextupdate = int(time.time()) + (60 * 10)
                        print("Next API Update",self.nextupdate)
                return self.lasttemp

        def getForecast(self):
                forecastURL = "http://api.openweathermap.org/data/2.5/onecall"
                PARAMS = { 'appid':settings.api_key, 'lat':'42.5', 'lon':'-83.18' }
                if self.forecastupdate < time.time():
                        output = [] 
                        print("Updating Weather forecast information from API")
                        r = requests.get(url = forecastURL, params = PARAMS) 
                        jsonData = json.loads(r.text)
                        output.append({'date': json.dumps(jsonData['daily'][0]['dt']), 'high' : json.dumps(jsonData['daily'][0]['temp']['max']), 'low':json.dumps(jsonData['daily'][0]['temp']['min']), 'icon': json.dumps(jsonData['daily'][0]['weather'][0]['main'])})
                        print(json.dumps(output))
                        output.append({'date': json.dumps(jsonData['daily'][1]['dt']), 'high' : json.dumps(jsonData['daily'][1]['temp']['max']), 'low':json.dumps(jsonData['daily'][1]['temp']['min']), 'icon':json.dumps(jsonData['daily'][1]['weather'][0]['main'])})
                        output.append({'date': json.dumps(jsonData['daily'][2]['dt']), 'high' : json.dumps(jsonData['daily'][2]['temp']['max']), 'low':json.dumps(jsonData['daily'][2]['temp']['min']), 'icon':json.dumps(jsonData['daily'][2]['weather'][0]['main'])})
                        self.lastforecast = output 
                        self.forecastupdate = int(time.time()) + (60 * 60)
                        print("Next Forecast API Update",self.forecastupdate)
                        print(json.dumps(output))
                return self.lastforecast
