"""
Command-line commands that operate on message queues.
"""

import json
from asyncio import get_event_loop, sleep
from logging import getLogger
from os import environ

from aio_pika import connect_robust, ExchangeType, Message

# pylint: disable=invalid-name
logger = getLogger(__name__)

# pylint: disable=too-few-public-methods
class DrainSQS:
    """
    Drain events from SQS,  log them in arangodb,  and post them to the AMQP (rabbitmq)
    queue.

    """
    def __init__(self, config):
        self._prefixes = {}
        self.config = config
        self.sqs = self._connect_to_sqs()
        adb = self._connect_to_adb()
        self.collection = adb.collection("sqs_events")
        self.aqmp = None

    def _connect_to_adb(self):
        from arango import ArangoClient
        client = ArangoClient(**self.config["arangodb"]["events"]["client"])
        return client.db(**self.config["arangodb"]["events"]["database"])

    def _connect_to_sqs(self):
        from boto3 import client
        return client(
            "sqs",
            aws_access_key_id=self.config["aws"]["aws_access_key_id"],
            aws_secret_access_key=self.config["aws"]["aws_secret_access_key"],
            region_name=self.config["aws"]["region_name"]
        )

    async def do(self, parameters):
        """
        Loop on SQS queue,  processing events produced by smartthings system

        :param parameters: always empty for this command
        :return:
        """
        if parameters:
            raise ValueError("process_sensor_events takes no parameters")

        poll_error_count = 0
        connection = await connect_robust(
            loop=get_event_loop(),
            **self.config["pika"]
        )
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange("smartthings", ExchangeType.FANOUT)
            while True:
                # pylint: disable=broad-except
                try:
                    await self._poll_sqs(exchange)
                    poll_error_count = 0
                except Exception:
                    logger.error("Error while polling SQS", exc_info=True)
                    poll_error_count += 1
                    if poll_error_count > 1:
                        logger.error("%d consecutive errors polling from SQS queue"
                                     , poll_error_count)

                    await sleep(10)
                    continue

    async def _poll_sqs(self, exchange):
        logger.debug("Waiting to receive messages from SQS queue")
        response = self.sqs.receive_message(
            QueueUrl=self.config["aws"]["queue_url"],
            MaxNumberOfMessages=10,
            WaitTimeSeconds=int(environ.get("WAIT_TIME_SECONDS", 20))
        )
        event_batch = []
        delete_batch = []
        if "Messages" not in response:
            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                logger.error("Got error while receiving queue messages; response: %s", response)
                raise RuntimeError("Error receiving queue messages")
        else:
            logger.debug("Received %d messages from SQS queue", len(response["Messages"]))
            for message in response["Messages"]:
                delete_batch.append({
                    "Id": message["MessageId"],
                    "ReceiptHandle": message["ReceiptHandle"]
                })
                body = json.loads(message["Body"])
                for event in body:
                    device_event = dict(event["deviceEvent"])
                    device_event["_key"] = device_event["eventId"]
                    device_event["eventTime"] = event["eventTime"]
                    del device_event["eventId"]
                    event_batch.append(device_event)

            logger.debug("Inserting messages into arangodb")
            self.collection.insert_many(event_batch)
            logger.debug("Inserting messages into rabbitmq")
            for event in event_batch:
                message = Message(body=json.dumps(event).encode("ascii"))
                await exchange.publish(message, routing_key=event["attribute"])

            logger.debug("Delete messages from SQS")
            self.sqs.delete_message_batch(
                QueueUrl=self.config["aws"]["queue_url"],
                Entries=delete_batch
            )
        return event_batch
