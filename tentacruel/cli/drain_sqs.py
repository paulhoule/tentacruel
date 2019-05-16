"""
Command-line commands that operate on message queues.
"""

import json
from asyncio import get_event_loop, sleep
from logging import getLogger

from aio_pika import connect_robust, ExchangeType, Message

# pylint: disable=invalid-name
from tentacruel.sqs import SqsQueue

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
        self.sqs = SqsQueue(config)

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
        messages = self.sqs.receive()
        event_batch = []
        delete_batch = []
        if messages:
            for message in messages:
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

            logger.debug("Inserting messages into rabbitmq")
            for event in event_batch:
                message = Message(body=json.dumps(event).encode("ascii"))
                await exchange.publish(message, routing_key=event["attribute"])

            logger.debug("Delete messages from SQS")
            self.sqs.delete(delete_batch)

        return event_batch
