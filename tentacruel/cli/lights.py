"""
Commands for controlling the lights.  Physically separate from run.py so we have
a sane way to add or remove new commands that we can firm up over time.
"""

import re
from asyncio import sleep
from typing import List
from phue import Bridge

# pylint: disable=too-few-public-methods
class LightCommands:
    """
    Object for executing command-line commands associated with Hue Lights.
    """
    #
    # only numeric for now
    #
    attributes = {
        "transitiontime",
        "brightness",
        "colortemp",
        "colortemp_k",
        "hue",
        "saturation"
    }

    def __init__(self, parent):
        self.parent = parent
        self.bridge = None

    def _ensure_bridge(self):
        if not self.bridge:
            self.bridge = Bridge()

    # pylint: disable=invalid-name
    async def do(self, parameters: List[str]):
        """
        Implement light control commands such as the following::

           light 4 on
           light group 3 hue 7712

        in which case this function receive the parameters::

           ["4","on"]
           ["group","3","hue","7712"]

        :param parameters:
        :return:
        """
        self._ensure_bridge()

        idx = 0
        first = parameters[idx]
        idx += 1
        pattern = re.compile("[0-9]+")
        if pattern.match(first):
            light_id = int(first)
            light = self.bridge.lights[light_id - 1]
        elif first == "group":
            second = parameters[idx]
            idx += 1
            group_id = int(second)
            light = self.bridge.groups[group_id - 1]
        else:
            raise ValueError("the light command must be followed by "
                             "a number or by 'group' and then a number")

        while idx < len(parameters):
            cmd = parameters[idx]
            idx += 1
            if cmd == "on":
                light.on = True
            elif cmd == "off":
                light.on = False
            elif cmd in LightCommands.attributes:
                amount = int(parameters[idx])
                idx += 1
                setattr(light, cmd, amount)
            else:
                raise ValueError(f"Command {cmd} is not available for lights")

    async def get_unreachable_lights(self, lights, wait_time=10, tries=3):
        """
        Detect unavailable lights.  Every so often a ping fails (for instance when there
        is a lot of Wi-Fi activity) so we will wait and retry to make sure.  Default
        settings are based on a small amount of experience with how rapidly the Hue
        system seems to respond to lights having the AC power turned on and off

        :param lights: list or set of integer light ids
        :param wait_time: how many seconds to wait to try pinging lights a second time
        :param tries: how many tries to try the ping before giving up
        :return: set of unavailable lights
        """

        self._ensure_bridge()
        available = set()
        lights = set(map(int, lights))
        for attempt in range(tries):
            unavailable = lights - available
            if not unavailable:
                return set()

            if attempt:
                await sleep(wait_time)

            for light in lights - available:
                if self.bridge.get_light(light)['state']['reachable']:
                    available.add(light)

        return lights - available
