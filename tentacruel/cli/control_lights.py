# pylint: disable=invalid-name
"""
Command-line commands that operate on message queues.
"""
import json
from asyncio import get_event_loop, sleep, gather
from logging import getLogger

from aio_pika import connect_robust, ExchangeType
from tentacruel.cli import LightZone

logger = getLogger(__name__)
# pylint: disable=too-few-public-methods
class ControlLights:
    """
    Implementation of Command Line command to drain events from rabbitmq and have
    appropriate side effects on the lights!
    """
    def __init__(self, config, lights):
        self._prefixes = {}
        self.config = config
        # pylint: disable=protected-access
        self.bridge = lights._bridge

        self.zones = [
            LightZone(
                self.send_to_hue,
                timeouts={"bottom": 60, "top": 120}
            )
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
        async with connection:
            channel = await connection.channel()

            exchange = await channel.declare_exchange(
                'smartthings',
                ExchangeType.FANOUT
            )

            queue = await channel.declare_queue(exclusive=True)
            await queue.bind(exchange, routing_key="motion")

            await gather(
                self._respond_to_messages(queue),
                self._periodic_ticks()
            )

    async def _respond_to_messages(self, queue):
        async with queue.iterator() as messages:
            async for message in messages:
                with message.process():
                    for zone in self.zones:
                        event = json.loads(message.body)
                        await zone.on_event(event, get_event_loop().time())

    async def _periodic_ticks(self):
        """
        Polling for timeouts might not be ideal,  but it means we can reuse our
        tests.

        Some design notes:

        One disadvantage of an N-second tick is that we might want to schedule
        events that unfold more quickly than that.  For instance,  if we want to do
        a complex animation with the lights we need shorted timesteps.  Also the
        callback style would get awkward if we were doing anything more complex
        than what we are doing.

        Assuming however,  that timeouts are the usual use case we need a way to
        cancel them,  for instance,  if we have a 60 second timeout to turn off
        the lights but there is another motion event,  we need to cancel the timeout.

        Our polling strategy is one way to do that,  but it may be possible to
        tell the event loop to not run the future tsak at all or alternatively set a
        flag that tells the timeout "thread" to give up.

        :return:
        """
        while True:
            await sleep(10)
            for zone in self.zones:
                await zone.on_tick(get_event_loop().time())


    def send_to_hue(self, commands):
        """
        Send commands ro hue

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
