# pylint: disable=missing-docstring

class LightZone:
    """
    Starting to shape up architecturally,  might event have it be testable!

    This class represents a set of lights whose on-and-off behavior in response to
    motion is related to each others.  It clusters all of the state involved in one
    place.

    """
    VERTICAL = "vertical"
    INDEPENDENT = "independent"

    def __init__(self, effector):
        self.effector = effector
        self.major = LightZone.INDEPENDENT
        self.light_zones = {
            'downstairs-hallway': 'bottom',
            'upstairs-north': 'top',
            'upstairs-south': 'top'
        }

        self.sensor_zones = {
            "upstairs-south": 'top',
            "upstairs-north": 'top',
            "upstairs-mid": 'top',
            "downstairs-hallway": 'bottom'
        }

        self._hue_targets = {
            "upstairs-north": 2,
            "upstairs-south": 3,
            "downstairs-hallway": 6
        }

        self.sensors = {
            "a76876ab-6ded-4fb5-9955-76dd0cbb6525": "upstairs-south",
            "c9d2e33e-258b-48c5-af1a-29a95f189d80": "upstairs-north",
            "bf423230-3495-4375-8033-60b4f7d3455c": "upstairs-mid",
            "a20bab2e-a7d0-4c93-8723-27a7bf3299b6": "downstairs-hallway"
        }

        self.timeouts = {
            "bottom": 200,
            "top": 500,
        }

        self.alarms = {
            "bottom": None,
            "top": None,
        }

    def on_event(self, event, when):
        """

        :param event:
        :return:
        """
        if event["attribute"] != "motion":
            return

        device_id = event["deviceId"]
        if device_id not in self.sensors:
            return

        sensor = self.sensors[device_id]
        state = event["value"]

        if state == "active":
            commands = []
            zone = self.sensor_zones[sensor]
            for light, light_zone in self.light_zones.items():
                if light_zone == zone:
                    light_id = self._hue_targets[light]
                    commands.append(('l', light_id, 'on', True))

            self.effector(commands)
        else:
            zone = self.sensor_zones[sensor]
            self.alarms[zone] = when + self.timeouts[zone]

    def on_tick(self, when):
        """

        :param when:
        :return:
        """
        commands = []
        for zone,alarm in self.alarms.items():
            if alarm and  when >= alarm:
                for light, light_zone in self.light_zones.items():
                    if light_zone == zone:
                        light_id = self._hue_targets[light]
                        commands.append(('l', light_id, 'on', False))
                self.alarms[zone] = None

        if commands:
            self.effector(commands)

    def execute(self, commands):
        """
        The commands here are tuples of the form ("l", light_id, parameter, value)
        if it is a light number and "g" if it is a group number.  These are
        passed through a central point so they can logged,  mocked,  etc.

        :param commands:
        :return:
        """
        self.effector(commands)
