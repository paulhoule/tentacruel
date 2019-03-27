"""
Script for AVR application
"""

from asyncio import get_event_loop
from logging import getLogger, StreamHandler
from os import environ

from tentacruel.avr import AvrControl

async def power_control():
    """
    Determine what the power and zone status is for the receiver

    :return:
    """
    control = AvrControl("192.168.0.10")
    await control.setup()
    status = await control.is_heos_on()
    print(status)
    await control.shutdown()

if __name__ == "__main__":
    if "LOGGING_LEVEL" in environ:
        getLogger(None).setLevel(environ["LOGGING_LEVEL"])

    getLogger(None).addHandler(StreamHandler())

    # pylint: disable=invalid-name
    loop = get_event_loop()
    loop.run_until_complete(power_control())
    loop.close()
