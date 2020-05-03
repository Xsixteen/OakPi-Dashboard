import requests
import json

class GateStatus:

        def getGateStatus(self):
                currentGateStatusURL = "http://192.168.50.100:8080/api/v1/gatestatus/latest"
                print("Updating Gate Status information from API")
                r = requests.get(url = currentGateStatusURL) 
                jsonData = json.loads(r.text)
                jsonGateStat = jsonData["gatestatus"]
                jsonEventTime = jsonData["eventTime"]
                GATESTAT = {'gatestatus':json.dumps(jsonGateStat), 'time':json.dumps(jsonEventTime)};
                return GATESTAT;

