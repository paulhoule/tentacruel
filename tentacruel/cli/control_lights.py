# pylint: disable=invalid-name
"""
Command-line commands that operate on message queues.
"""

from asyncio import get_event_loop
from logging import getLogger

from aio_pika import connect_robust, ExchangeType

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
                        print(message.body)
