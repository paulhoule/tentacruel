from tentacruel.config import get_config
import requests

config = get_config()

class LIFX(object):
    def __init__(self):
        self.token = config["lifx"]["personal_access_token"]

    def get_status(self):
        token = self.token
        headers = {
            "Authorization": "Bearer %s" % token,
        }
        response = requests.get('https://api.lifx.com/v1/lights/all', headers=headers)
        print(response.json())

    def power_on(self):
        token = self.token
        headers = {
            "Authorization": "Bearer %s" % token,
        }
        payload = {
            "power": "on",
        }
        response = requests.put('https://api.lifx.com/v1/lights/all/state',
                                data=payload, headers=headers)
        print(response.json())

    def power_off(self):
        token = self.token
        headers = {
            "Authorization": "Bearer %s" % token,
        }
        payload = {
            "power": "off",
        }
        response = requests.put('https://api.lifx.com/v1/lights/all/state',
                                data=payload, headers=headers)
        print(response.json())
