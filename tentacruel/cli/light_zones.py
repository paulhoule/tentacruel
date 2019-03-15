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
            key : None
            for key in self.timeouts
        }

        self.states = config.get("states", ["singleton"])
        self.state = None

    async def setup(self):
        """
        Turn off all the lights at the very beginning.

        :return:
        """
        commands = [
            ("l", light, 'on', False) for light in self.lights.values()
        ]
        self.effector(commands)
        self.state = self.states[0]

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
        value = event["value"]

        if value == "active":
            zone = self.sensor_zones[sensor]
            off_zones = set()
            commands = []
            if self.state == "dark" and zone == "bottom":
                zone = "vertical"
                self.state = "vertical"
                self.alarms["vertical"] = when + self.timeouts["vertical"]
            elif self.state == "vertical" and zone == "top":
                zone = "top"
                off_zones = {"bottom"}
                self.alarms["vertical"] = None
                self.state = "independent"
            else:
                self.state = "independent"

            for light in self.light_zones[zone]:
                light_id = self.lights[light]
                commands.append(('l', light_id, 'on', True))

            for off_zone in off_zones:
                for light in self.light_zones[off_zone]:
                    light_id = self.lights[light]
                    commands.append(('l', light_id, 'on', False))

            self.effector(commands)
        else:
            zone = self.sensor_zones[sensor]
            self.alarms[zone] = when + self.timeouts[zone]

    async def on_tick(self, when):
        """

        :param when: timestamp in seconds counting upwards.  This could be the Unix epoch or
                     it could be a countup local to a thread
        :return:
        """
        commands = []
        for zone, alarm in self.alarms.items():
            if alarm and  when >= alarm:
                if zone == "vertical":
                    self.state = "independent"
                    bottom = set(self.light_zones["bottom"])
                    vertical = set(self.light_zones["vertical"])
                    for light in vertical - bottom:
                        light_id = self.lights[light]
                        commands.append(('l', light_id, 'on', False))
                else:
                    for light in self.light_zones[zone]:
                        light_id = self.lights[light]
                        commands.append(('l', light_id, 'on', False))
                self.alarms[zone] = None

        if all([not then for then in self.alarms.values()]):
            self.state = "dark"

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
