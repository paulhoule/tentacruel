"""
Capture events from rabbitmq and log them into arangodb

"""
import json
from asyncio import get_event_loop
from logging import getLogger, StreamHandler
from os import environ
from pathlib import Path

import yaml
from aio_pika import connect_robust, ExchangeType

# pylint: disable=invalid-name
from arango import DocumentInsertError, DocumentUpdateError

logger = getLogger(__name__)

def connect_to_adb(config):
    """
    Connect to arango database

    :param config:
    :return:
    """
    from arango import ArangoClient
    client = ArangoClient(**config["arangodb"]["events"]["client"])
    return client.db(**config["arangodb"]["events"]["database"])

class LogToADB:
    """
    Application that loads events from RabbitMQ into arangodb database

    """
    def __init__(self):
        if "LOGGING_LEVEL" in environ:
            getLogger(None).setLevel(environ["LOGGING_LEVEL"])

        getLogger(None).addHandler(StreamHandler())
        with open(Path.home() / ".tentacruel" / "config.yaml") as a_stream:
            self.config = yaml.load(a_stream)
        adb = connect_to_adb(self.config)
        self.collection = adb.collection("sqs_events")
        self.attributes = adb.collection("attributes")
        self.connection = None

    async def setup(self):
        """
        Initialization that can only be completed in an async method
        """
        self.connection = await connect_robust(
            loop=get_event_loop(),
            **self.config["pika"]
        )

    async def log_events(self):
        """
        Get events from Q and log them in the database

        :return:
        """
        await self.setup()
        async with self.connection:
            channel = await self.connection.channel()

            exchange = await channel.declare_exchange(
                'smartthings',
                ExchangeType.FANOUT
            )

            queue = await channel.declare_queue(exclusive=True)
            await queue.bind(exchange, routing_key="")
            async with queue.iterator() as messages:
                async for message in messages:
                    with message.process():
                        event = json.loads(message.body)
                        logger.debug("Received event: %s", event)
                        try:
                            self.collection.insert(event, silent=True)
                        except DocumentInsertError as error:
                            if error.error_code != 1210:
                                raise
                        if "attribute" in event and "value" in event:
                            packet = {
                                "_key": event["deviceId"],
                                event["attribute"]: {
                                    "value": event["value"],
                                    "eventTime": event["eventTime"]
                                }
                            }

                            try:
                                self.attributes.update(packet, silent=True)
                            except DocumentUpdateError as error:
                                if error.error_code != 1202:
                                    raise
                                self.attributes.insert(packet, silent=True)
