"""
Routine that uses ping for presence detection in the LAN

"""

import platform    # For getting the operating system name
import subprocess  # For executing a shell command
import sys
from asyncio import run, set_event_loop_policy
from asyncio.subprocess import PIPE, STDOUT, create_subprocess_exec
from logging import getLogger, StreamHandler
from os import environ
from pathlib import Path

import yaml
from arango import aql

# pylint: disable=invalid-name
logger = getLogger(__name__)

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

async def ping_all():
    """
    Ping every host on our list

    :return:
    """

    if "LOGGING_LEVEL" in environ:
        getLogger(None).setLevel(environ["LOGGING_LEVEL"])

    getLogger(None).addHandler(StreamHandler())
    with open(Path.home() / ".tentacruel" / "config.yaml") as a_stream:
        config = yaml.load(a_stream)

    adb = connect_to_adb(config)
    cursor = adb.aql.execute("""
        FOR row in pingables
           FILTER NOT row.disabled
           return row._key
    """)
    targets = {key for key in cursor}
    retry_count = 3
    seen = await ping_targets(retry_count, targets)
    updates = [
        {"_key": key, "visible": value}
        for (key, value) in seen.items()
    ]
    adb.collection("pingables").update_many(updates)

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
            print(f"{target} {responded}")
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


if __name__ == "__main__":
    ensure_proactor()
    run(ping_all())
