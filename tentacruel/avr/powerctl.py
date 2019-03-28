"""
Script for AVR application
"""

from asyncio import get_event_loop
from logging import getLogger, StreamHandler
from os import environ
from sys import argv
from typing import List

from tentacruel.avr import AvrControl

async def power_control():
    """
    Determine what the power and zone status is for the receiver or set it.

    Here are the command line examples::

       '' (empty string)     print status
       'zone1 on'            turn zone1 on
       'zone2 off'           turn zone2 off
       'zone1 zone2 on'      both zones on
       'zone1 off zone2on'  what it looks like

    The assumption here is that if we are turning zones on we want to use them with HEOS.  If a zone
    is not specified,  we leave it as is.

    :return:
    """

    zones = parse_argv(argv[1:])

    control = AvrControl("192.168.0.10")
    await control.setup()
    if zones:
        await control.set_power_status(zones)
    else:
        status = await control.is_heos_on()
        print(status)
    await control.shutdown()


def parse_argv(arguments: List[str]):
    """
    Convert command line arguments (as a list of strings) to a
    dictionary of which zone is to be turned on True or off False

    :param arguments:
    :return:
    """
    zones = {}
    current_zones = set()
    for term in arguments:
        if term in ("1", "z1", "zone1", "main", "Room23"):
            current_zones.add(1)
        elif term in ("2", "z2", "zone2", "hallway"):
            current_zones.add(2)
        elif term == "all":
            current_zones.update({1, 2})
        elif term in ("on", "off"):
            if not current_zones:
                if zones:
                    raise ValueError("cannot put two power states in a row")
                else:
                    raise ValueError("power state not preceded by one or more zone ids")

            for zone in current_zones:
                if zone in zones:
                    raise ValueError("cannot set power state for a zone more than once")
                zones[zone] = (term == "on")
            current_zones = set()
    return zones


if __name__ == "__main__":
    if "LOGGING_LEVEL" in environ:
        getLogger(None).setLevel(environ["LOGGING_LEVEL"])

    getLogger(None).addHandler(StreamHandler())

    # pylint: disable=invalid-name
    loop = get_event_loop()
    loop.run_until_complete(power_control())
    loop.close()
