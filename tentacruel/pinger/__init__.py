"""
Routine that uses ping for presence detection in the LAN

"""
import datetime
import json
import platform    # For getting the operating system name
import subprocess  # For executing a shell command
import sys
from asyncio import run, set_event_loop_policy, get_event_loop, sleep
from asyncio.subprocess import PIPE, STDOUT, create_subprocess_exec
from logging import getLogger, StreamHandler
from os import environ
from pathlib import Path
from uuid import uuid5, UUID, uuid3, uuid4

import yaml
from aio_pika import connect_robust, ExchangeType, Message
from arango import aql

# pylint: disable=invalid-name
logger = getLogger(__name__)

def iso_zulu_now():
    """
    Current UTC (Zulu) time

    :return:
    """
    return datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"

async def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    process = await create_subprocess_exec(*command, stdout=PIPE, stderr=STDOUT)
    (stdout, _) = await process.communicate()
    logger.debug("Pinged %s and got message %s", host, stdout)
    logger.debug("Pinged %s and got returncode %s", host, process.returncode)
    if process.returncode:
        return False

    return stdout.find(b"unreachable.") == -1


def connect_to_adb(config):
    """
    Connect to arango database

    :param config:
    :return:
    """
    from arango import ArangoClient
    client = ArangoClient(**config["arangodb"]["events"]["client"])
    return client.db(**config["arangodb"]["events"]["database"])

class Pinger:
    """
    Implementation of the application that does periodic logging and pings.

    """
    def __init__(self, retry_count=3):
        if "LOGGING_LEVEL" in environ:
            getLogger(None).setLevel(environ["LOGGING_LEVEL"])

        getLogger(None).addHandler(StreamHandler())
        with open(Path.home() / ".tentacruel" / "config.yaml") as a_stream:
            self.config = yaml.load(a_stream)
        self.adb = connect_to_adb(self.config)
        self.private_network_id = UUID(self.config["private_network_id"])
        self.retry_count = retry_count
        self.connection = None

    async def setup(self):
        """
        Initialization that can only be completed in an async method
        """
        self.connection = await connect_robust(
            loop=get_event_loop(),
            **self.config["pika"]
        )

    async def ping_all(self):
        """
        Ping every host on our list over and over again

        :return: None
        """
        await self.setup()
        async with self.connection:
            while True:
                await self.ping_all_once()
                await sleep(60)

    async def ping_all_once(self):
        """
        Ping all hosts once

        :return: None
        """
        exchange = await self.connect_to_exchange()
        cursor = self.adb.aql.execute("""
                FOR row in pingables
                   FILTER NOT row.disabled
                   return [row._key,row.visible]
            """)
        targets = dict(cursor)
        seen = await ping_targets(self.retry_count, targets.keys())
        update_adb = []
        events = []
        for host, visible in seen.items():
            this_moment = iso_zulu_now()
            delta = {
                "_key": host,
                "visible": visible,
                "lastObservedTime": this_moment,
            }
            if visible != targets[host]:
                delta["lastChangedTime"] = this_moment

                event = await self.create_event_packet(host, this_moment, visible)
                events.append(event)

            update_adb.append(delta)
        self.adb.collection("pingables").update_many(update_adb)
        for event in events:
            message = Message(body=json.dumps(event).encode("ascii"))
            await exchange.publish(message, routing_key=event["attribute"])

    async def connect_to_exchange(self):
        """
        Connect to exchange
        :return: AQMP exchange
        """
        channel = await self.connection.channel()
        exchange = await channel.declare_exchange("smartthings", ExchangeType.FANOUT)
        return exchange

    async def create_event_packet(self, host, this_moment, visible):
        """
        Create an event packet to send to the smartthings system


        :param host:
        :param private_network_id:
        :param this_moment:
        :param visible:
        :return:
        """
        device_id = uuid5(self.private_network_id, host)
        event_id = uuid4()
        event = {
            "_key": str(event_id),
            "deviceId": str(device_id),
            "attribute": "o2.reachable",
            "value": visible,
            "eventTime": this_moment,
        }
        return event


async def ping_targets(retry_count, targets):
    """
    Ping targets with up to ``retry_count`` attempts.

    :param retry_count: number of attempts made to contact host
    :param targets: iterable of strings,  ip addresses of targets
    :return:
    """
    unseen_targets = set(targets)
    for _ in range(retry_count):
        for target in list(unseen_targets):
            logger.debug("Pinging %s", target)
            responded = await ping(target)
            if responded:
                unseen_targets.remove(target)
    seen = {}
    for target in targets:
        seen[target] = target not in unseen_targets
    return seen


def ensure_proactor():
    """
    On Windows we get the selector event loop by default,  which does quite a few things,
    but it doesn't do I/O to subprocesses.  Therefore,  this routine will select the
    proactor event loop if we are running on Windows.

    :return: None
    """
    if sys.platform == 'win32':
        from asyncio import WindowsProactorEventLoopPolicy
        set_event_loop_policy(WindowsProactorEventLoopPolicy())