"""
Encapsulation of SQS access for tenacruel.  Specifically,  access to the SQS queue
which holds mesages coming in from the smartthings system.

"""
from logging import getLogger
from os import environ
from typing import List

from tentacruel.config import connect_to_sqs

LOGGER = getLogger(__name__)

class SqsQueue:
    """
    Represents an SQS queue with higher-level methods.

    """

    def __init__(self, config):
        """
        Constructor

        :param config: application config dictionary
        """
        self.sqs = connect_to_sqs(config)
        self.url = config["aws"]["queue_url"]

    def count(self) -> int:
        """
        Return approximate count of messages in queue.  Includes available,  not visible and
        delayed messages

        :return: count of messages
        """
        attributes = self.sqs.get_queue_attributes(
            QueueUrl=self.url,
            AttributeNames=[
                "ApproximateNumberOfMessages",
                "ApproximateNumberOfMessagesNotVisible",
                "ApproximateNumberOfMessagesDelayed"
            ]
        )["Attributes"]

        return sum([int(value) for value in attributes.values()])

    def receive(self) -> List[str]:
        """
        Attempt to receive the maximum number of messages from the queue by long polling

        :return: List of messages
        """
        LOGGER.debug("Waiting to receive messages from SQS queue")
        response = self.sqs.receive_message(
            QueueUrl=self.url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=int(environ.get("WAIT_TIME_SECONDS", 20))
        )

        if "Messages" not in response:
            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                LOGGER.error("Got error while receiving queue messages; response: %s", response)
                raise RuntimeError("Error receiving queue messages")
            return []

        LOGGER.debug("Received %d messages from SQS queue", len(response["Messages"]))
        return response["Messages"]

    def delete(self, entries: List[dict]) -> None:
        """
        Delete messages from SQS queue,  the format of entries is::

            {
                "Id": "...",
                "ReceiptHandle": "..."
            }

        :param entries: a List of entries
        :return: Nothing
        """
        self.sqs.delete_message_batch(
            QueueUrl=self.url,
            Entries=entries
        )
