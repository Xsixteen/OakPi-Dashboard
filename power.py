import requests
import settings
import json
import time

class Power:
        def __init__(self):
                self.nextupdate = -1
                self.currentPower = None
                self.forecastupdate = -1

        def getCurrentPower(self):
                powerURL = "http://192.168.50.100:8080/api/v1/currentpower"
                if self.nextupdate < time.time():
                        print("Updating Power information from API")
                        r = requests.get(url = powerURL) 
                        jsonData = json.loads(r.text)

                        self.currentPower = jsonData["currentPowerUsageWatts"]
                        self.currentPowerUpdateTime = jsonData["updateTime"]
                 
                        self.nextupdate = int(time.time()) + (60 * 10)
                        print("Next API Update",self.nextupdate)
                return self