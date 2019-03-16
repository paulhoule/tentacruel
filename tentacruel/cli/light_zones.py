# pylint: disable=missing-docstring
# pylint: disable=missing-docstring

from logging import getLogger, DEBUG

LOGGER = getLogger()

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
        self.event_count = 0
        self.shadow = {}

    async def set_state(self, new_state):
        LOGGER.debug(
            "Event %d: transition from %s to %s",
            self.event_count,
            self.state,
            new_state)
        self.state = new_state

    async def set_alarm_for(self, system, when=None):
        self.alarms[system] = when
        LOGGER.debug("Event %d: set alarm %s for %s ", self.event_count, system, when)
        if LOGGER.isEnabledFor(DEBUG):
            for key, value in self.alarms.items():
                if value:
                    LOGGER.debug("Event %d: alarm for %s at %s", self.event_count, key, value)


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
        self.shadow = {
            light: False for light in self.lights.keys()
        }

    async def on_event(self, event, when):
        """

        :param event:
        :return:
        """
        if event["attribute"] != "motion":
            return

        self.event_count += 1
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
                await self.set_state("vertical")
                await self.set_alarm_for("vertical", when + self.timeouts["vertical"])
            elif self.state == "vertical" and zone == "top":
                zone = "top"
                off_zones = {"bottom"}
                await self.set_alarm_for("vertical")
                await self.set_state("independent")
            else:
                await self.set_state("independent")

            for light in self.light_zones[zone]:
                light_id = self.lights[light]
                self.shadow[light] = True
                commands.append(('l', light_id, 'on', True))

            for off_zone in off_zones:
                for light in self.light_zones[off_zone]:
                    light_id = self.lights[light]
                    self.shadow[light] = False
                    commands.append(('l', light_id, 'on', False))

            self.effector(commands)
        else:
            zone = self.sensor_zones[sensor]
            if self.state == "vertical" and zone == "bottom":
                zone = "vertical"

            await self.set_alarm_for(zone, when + self.timeouts[zone])

    async def on_tick(self, when):
        """

        :param when: timestamp in seconds counting upwards.  This could be the Unix epoch or
                     it could be a countup local to a thread
        :return:
        """
        self.event_count += 1
        commands = []
        for zone, alarm in self.alarms.items():
            if alarm and  when >= alarm:
                if zone == "vertical":
                    await self.set_state("independent")
                    bottom = set(self.light_zones["bottom"])
                    vertical = set(self.light_zones["vertical"])
                    for light in vertical - bottom:
                        light_id = self.lights[light]
                        self.shadow[light] = False
                        commands.append(('l', light_id, 'on', False))
                else:
                    for light in self.light_zones[zone]:
                        light_id = self.lights[light]
                        self.shadow[light] = False
                        commands.append(('l', light_id, 'on', False))
                await self.set_alarm_for(zone)

        if "dark" in self.states and self.state != 'dark':
            if all([not on_state for on_state in self.shadow.values()]):
                await self.set_state("dark")

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
