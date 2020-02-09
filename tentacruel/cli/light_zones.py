# pylint: disable=missing-docstring
# pylint: disable=missing-docstring

from logging import getLogger, DEBUG

LOGGER = getLogger()

# pylint: disable=too-many-instance-attributes
class LightZone:
    """
    Starting to shape up architecturally,  might even have it be testable!

    This class represents a set of lights whose on-and-off behavior in response to
    motion is related to each others.  It clusters all of the state involved in one
    place.

    """

    def __init__(self, effector, config):
        self.effector = effector
        self.key = config["key"]
        self.groups = {config["group"]}
        self.switches = {config["switch"]}

    async def setup(self):
        pass

    async def on_event(self, event, when):
        """

        :param event:
        :return:
        """

        if event["attribute"] not in {"switch", "level"}:
            return

        device_id = event["deviceId"]
        if device_id not in self.switches:
            return

        if event["attribute"] == "switch":
            is_on = event["value"] == "on"
            how_bright = 255
        else:
            is_on = True
            how_bright = (event["value"] * 255) // 100

        print("Sensor value is {value}");
        commands = []
        for group_id in self.groups:
            commands += [
                ('g', group_id, 'on', is_on, 0),
                ('g', group_id, 'bri', how_bright, 0)
            ]

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
