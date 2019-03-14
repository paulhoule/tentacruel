# pylint: disable=missing-docstring
# pylint: disable=too-many-instance-attributes
class LightZone:
    """
    Starting to shape up architecturally,  might event have it be testable!

    This class represents a set of lights whose on-and-off behavior in response to
    motion is related to each others.  It clusters all of the state involved in one
    place.

    """
    VERTICAL = "vertical"
    INDEPENDENT = "independent"

    def __init__(self, effector, config):
        self.effector = effector
        self.major = LightZone.INDEPENDENT
        self.light_zones = config["light_assignments"]
        self.sensor_zones = config["sensor_assignments"]
        self.lights = config["lights"]
        self.sensors = config["sensors"]
        self.timeouts = config["timeouts"]
        self.alarms = {
            "bottom": None,
            "top": None,
        }

    async def on_event(self, event, when):
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
                    light_id = self.lights[light]
                    commands.append(('l', light_id, 'on', True))

            self.effector(commands)
        else:
            zone = self.sensor_zones[sensor]
            self.alarms[zone] = when + self.timeouts[zone]

    async def on_tick(self, when):
        """

        :param when:
        :return:
        """
        commands = []
        for zone, alarm in self.alarms.items():
            if alarm and  when >= alarm:
                for light, light_zone in self.light_zones.items():
                    if light_zone == zone:
                        light_id = self.lights[light]
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
