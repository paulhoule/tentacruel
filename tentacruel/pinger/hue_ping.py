"""
Objects for pinging the Phillips Hue system to determine which lights are available and
what state they are in.

Temporary notes:

bedroom lights are::

    UUID('ae8df7bf-6903-5c41-aad6-de4aeb24dc87')
    UUID('2d424242-bf47-5e2f-b5ff-b325d2d8017d')
"""
import json
from asyncio import sleep, CancelledError
from pathlib import Path
from typing import Dict, Any, Coroutine, Callable
from uuid import UUID, uuid5, uuid4

from aio_pika import Exchange, Message
from aiohttp import ClientSession
from tentacruel import keep
from tentacruel.pinger import iso_zulu_now

HUE_NS = UUID('63b25700-662c-11e9-8c24-9eb6d06a70c5')

class AsyncHue():
    """
    Asynchronous wrapper for Hue API.

    This is not complete,  but it is sufficient for the pinger.

    """
    def __init__(self):
        config_file = Path.home() / ".python_hue"
        bridges = json.loads(config_file.read_bytes())
        if len(bridges) != 1:
            raise ValueError("This system supports exactly one Hue Bridge")

        self._bridge_ip = list(bridges.keys())[0]
        self._username = list(bridges.values())[0]["username"]
        self._session = ClientSession()

    async def get_lights(self) -> str:
        """
        Get information about all lights from the Hue system

        :return: string containing a JSON document;  keys are numeric light ids,  values are dicts
        that represent each light

        """
        url = f"http://{self._bridge_ip}/api/{self._username}/lights/"
        async with self._session.get(url) as response:
            return await response.text()

    async def teardown(self) -> None:
        """
        Close session

        :return: Nothing
        """
        await self._session.close()

class HuePinger():
    """
    Object for pinging lights in the Hue system to see if they are reachable,  on,  etc.

    """

    def __init__(self, exchange: Exchange):
        self._hue = AsyncHue()
        self._last_state = {}
        self.exchange = exchange

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._hue.teardown()

    async def poll(self) -> None:
        """
        Do a single round of polling of the Hue system.  Scans all lights.

        :return: Nothing
        """
        lights = json.loads(await self._hue.get_lights())
        for light in lights.values():
            light_uuid = uuid5(HUE_NS, light["uniqueid"])
            state = censor_state(light)
            this_moment = iso_zulu_now()
            if light_uuid not in self._last_state:
                for (attribute, value) in state.items():
                    await self.update_state(light_uuid, this_moment, attribute, value)
            else:
                last_state = self._last_state[light_uuid]
                for (attribute, value) in state.items():
                    if last_state[attribute] != value:
                        await self.update_state(light_uuid, this_moment, attribute, value)

            self._last_state[light_uuid] = state

    async def update_state(self, device_id: UUID, this_moment: str, attribute: str, value: Any)\
            -> None:
        """
        Update state of device

        :param device_id: UUID of device
        :param attribute: attribute name
        :param value: value of attribute,  typically a JSON Scalar (number, string or boolean)
        :return: nothing
        """

        event = self.create_event_packet(device_id, this_moment, attribute, value)
        message = Message(body=json.dumps(event).encode("ascii"))
        await self.exchange.publish(message, routing_key=event["attribute"])

    def create_event_packet(self, device_id, this_moment, attribute, value):
        # pylint: disable=no-self-use
        """
        Create a smartthings-comparable event packet

        """

        event_id = uuid4()
        event = {
            "_key": str(event_id),
            "deviceId": str(device_id),
            "attribute": f"hue.{attribute}",
            "value": value,
            "eventTime": this_moment,
        }
        return event


def censor_state(light: Dict[str, Any]):
    """
    Remove unwanted parameters from light state

    :param light: light configuration and status information from Hue Bridge
    :return: a few selected fields
    """
    return keep(light["state"], {"reachable", "on", "bri", "hue", "sat", "xy", "ct", "colormode"})

async def hue_loop(exchange: Exchange) -> None:
    """
    Asynchronous main method of command-line program.

    :return:
    """
    async with HuePinger(exchange) as pinger:
        while True:
            await pinger.poll()
            await sleep(10)

async def protect(that: Callable[[], Coroutine], restart_wait=10.0):
    """
    Create a coroutine that 'restarts' a coroutine when it fails.  The main
    use case is that the function inside can fail due to a transient external
    error.  In this case there are multiple tasks running and we want to keep
    the whole process running even though one process crashed.

    I put 'restart' in quotes because we can't quite restart a coroutine,  but
    we can start a new one.  To be able to do that,  we pass in `that` which
    is a function that returns a coroutine.

    This function catches every exception except for `CancelledError`, because
    it assumes that if the inner coroutine is cancelled.

    To borrow trouble:  shared resources could be a problem.  For instance,  we
    would like to share a database or message queue connection between multiple
    tasks.  If one of these connections is defective we ought to replace it,  then
    restart the dependencies.

    :param that: function that returns a coroutine
    :param restart_wait: time in seconds to wait before `restart`
    :return: return value of coroutine
    """
    while True:
        try:
            return await that()
        except CancelledError: # pylint: disable=try-except-raise
            raise
        except Exception: # pylint: disable=broad-except
            await sleep(restart_wait)
