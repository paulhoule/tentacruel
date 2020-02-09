# pylint: disable=invalid-name
"""
Command-line commands that operate on message queues.
"""
import json
from asyncio import get_event_loop, sleep, gather
from logging import getLogger

from aio_pika import connect_robust, ExchangeType
from phue import Bridge
from tentacruel.cli import LightZone

logger = getLogger(__name__)
# pylint: disable=too-few-public-methods
class ControlLights:
    """
    Implementation of Command Line command to drain events from rabbitmq and have
    appropriate side effects on the lights!
    """
    def __init__(self, config):
        self._prefixes = {}
        self.config = config
        # pylint: disable=protected-access
        self.bridge = Bridge()

        self.zones = [
            LightZone(
                self.send_to_hue,
                zone
            )
            for zone in config["zones"]
        ]

    async def do(self, parameters):
        """
        Loop over messages from smartthings to find motion events and use those to turn lights
        on and off

        :param parameters: empty list because this command has no parameters
        :return: Nothing
        """
        if parameters:
            raise ValueError("process_sensor_events takes no parameters")

        connection = await connect_robust(
            loop=get_event_loop(),
            **self.config["pika"]
        )

        for zone in self.zones:
            logger.debug("Setting up zone %s", zone.key)
            await zone.setup()

        async with connection:
            channel = await connection.channel()

            exchange = await channel.declare_exchange(
                'smartthings',
                ExchangeType.FANOUT
            )

            queue = await channel.declare_queue(exclusive=True)
            await queue.bind(exchange, routing_key="switch")
            await self._respond_to_messages(queue)

    async def _respond_to_messages(self, queue):
        async with queue.iterator() as messages:
            async for message in messages:
                with message.process():
                    event = json.loads(message.body)
                    for zone in self.zones:
                        await zone.on_event(event, get_event_loop().time())

    def send_to_hue(self, commands):
        """
        Send commands to hue

        :param commands:
        :return:
        """
        for (device_type, *arguments) in commands:
            if device_type == "l":
                self.bridge.set_light(*arguments)
            elif device_type == "g":
                self.bridge.set_group(*arguments)
            else:
                raise ValueError("l and g are the only allowed command types here")
