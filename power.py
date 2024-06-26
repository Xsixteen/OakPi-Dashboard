import requests
import settings
import json
import time

class Power:
        def __init__(self):
                self.nextupdate = -1
                self.currentPower = 0
                self.forecastupdate = -1
                self.currentPowerEpochTimeSeconds = -1

        def getCurrentPower(self):
                powerURL = "http://192.168.50.100:8080/api/v1/currentpower"
                if self.nextupdate < time.time():
                        print("Updating Power information from API")
                        try:
                                r = requests.get(url = powerURL) 
                        except requests.exceptions.RequestException as e:
                                print ("Error due to:", e) 
                                return self
                        jsonData = json.loads(r.text)

                        self.currentPower = jsonData["currentPowerUsageWatts"]
                        self.currentPowerUpdateTime = jsonData["updateTime"]
                        self.currentPowerEpochTimeSeconds = jsonData["epochSeconds"]
 
                        self.nextupdate = int(time.time()) + (60 * 1)
                        print("Next API Update",self.nextupdate)
                return self
