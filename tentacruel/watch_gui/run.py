"""

GUI application to watch system status.

"""
import asyncio
from asyncio import run, get_event_loop, create_task
from logging import getLogger, StreamHandler
from os import environ
from tkinter import Button, TclError, Label
from typing import Any, Dict
import json

from aio_pika import connect_robust, Connection, ExchangeType
from tentacruel.config import get_config
from tentacruel.gui import ManagedGridFrame

QUIT_BUTTON = "quit_button"
LOGGER = getLogger(__name__)

# pylint: disable=invalid-name
async def run_tk(root, interval=0.05) -> None:
    '''
    Run a tkinter app in an asyncio event loop.
    '''
    try:
        while root.alive:
            root.update()
            await asyncio.sleep(interval)
    except TclError as e:
        if "application has been destroyed" not in e.args[0]:
            raise

def extract_sensor_list(config: Dict[str, Any]):
    """
    Find sensors in configuration file and return them as a list

    :param config: configuration megadictionary
    :return: a list of dicts that look like::

        {
            "sensor_id": "a20bab2e-a7d0-4c93-8723-27a7bf3299b6",
            "name": "inner-doghouse"
        }

        defining what sensors to show in GUI.
    """
    zones = config["zones"]
    sensors = []
    for zone in zones:
        if "sensors" in zone:
            for (sensor_id, name) in zone["sensors"].items():
                sensors.append({
                    "sensor_id": sensor_id,
                    "name": name
                })
    return sensors


# pylint: disable=too-many-ancestors
class Application(ManagedGridFrame):
    """
    This application shows a visual display of the system state,  for instance,
    the state of the motion detectors,  and updates the image as messages
    come in on the queue.

    """

    def __init__(self, config: Dict[str, Any], **kwargs):
        """

        :param config: tentacruel configuration dictionary;  this is not saved
        in the constructor.  But the constructor may validate it and set other
        variables in response to the configuration
        """
        kwargs["columns"] = 2
        super().__init__(**kwargs)
        self.alive = True
        self._pika_config = config["pika"]
        self.connection: Connection = None

        sensors = extract_sensor_list(config)
        for sensor in sensors:
            self._add(sensor["sensor_id"] + "-label", Label, text=sensor["name"])
            self._add(sensor["sensor_id"] + "-status", Label, text="Unknown")

        self._add(QUIT_BUTTON, Button, text="Quit", width=15, height=1, columnspan=1)

    async def setup(self) -> None:
        """
        Setup stage completed asynchronously so we can use asynchronous
        facilities to do th e setup

        :return:
        """
        create_task(self.listen_on_queue())

    async def listen_on_queue(self):
        """
        Loop on message queue to get motion events and pass to GUI

        :return:
        """
        connection: Connection = await connect_robust(
            loop=get_event_loop(),
            **self._pika_config
        )

        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                'smartthings',
                ExchangeType.FANOUT
            )

            queue = await channel.declare_queue(exclusive=True)
            await queue.bind(exchange, routing_key="motion")

            async with queue.iterator() as messages:
                async for message in messages:
                    with message.process():
                        event = json.loads(message.body)
                        print(event)


async def amain() -> None:
    """
    amain is a main method,  but it is asynchronous,  main() jumps into here
    right away where we initialize the application and then start polling
    the tk event loop to handle gui events together with asyncio

    :return:
    """
    config = get_config()
    app = Application(config)
    await app.setup()
    await run_tk(app)

def main() -> None:
    """
    main method of application,  expressed as a function so pylint won't
    complain about how I use the main namespace.  Boots asynchronous main
    method inside default event loop.

    :return:
    """
    if "LOGGING_LEVEL" in environ:
        getLogger(None).setLevel(environ["LOGGING_LEVEL"])
    getLogger(None).addHandler(StreamHandler())

    run(amain())

if __name__ == "__main__":
    main()
