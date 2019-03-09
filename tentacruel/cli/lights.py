"""
Commands for controlling the lights.  Physically separate from run.py so we have
a sane way to add or remove new commands that we can firm up over time.
"""

import re
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
        self._bridge = Bridge()

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
        idx = 0
        first = parameters[idx]
        idx += 1
        pattern = re.compile("[0-9]+")
        if pattern.match(first):
            light_id = int(first)
            light = self._bridge.lights[light_id - 1]
        elif first == "group":
            second = parameters[idx]
            idx += 1
            group_id = int(second)
            light = self._bridge.groups[group_id - 1]
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

    def _get_unreachable_lights(self, group_name):
        that = self._bridge.get_group(group_name)
        not_available = set()
        for light in map(int, that['lights']):
            if not self._bridge.get_light(light)['state']['reachable']:
                not_available.add(light)
        return not_available
