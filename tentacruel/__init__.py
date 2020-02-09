# pylint: disable=missing-docstring
# pylint: disable=invalid-name

"""
Module to control Denon/Marantz
"""

import json
from json import JSONDecodeError
from asyncio import create_task, open_connection, StreamReader, StreamWriter, iscoroutine, iscoroutinefunction
from asyncio import get_event_loop, Future, CancelledError
from typing import Dict, Set
from urllib.parse import parse_qs
from logging import getLogger

from tentacruel.service import _HeosService, HeosError
from tentacruel.system import _HeosSystem
from tentacruel.browse import _HeosBrowse
from tentacruel.player import _HeosPlayer
from tentacruel.group import _HeosGroup

def keep(source: Dict, keep_keys: Set):
    return {key: value for (key, value) in source.items() if key in keep_keys}

def discard(source: Dict, discard_keys: Set):
    return {key: value for (key, value) in source.items() if key not in discard_keys}

def create_future():
    return get_event_loop().create_future()

HEOS_PORT = 1255

LOCAL_MUSIC = 1024
PLAYLISTS = 1025
HISTORY = 1026
AUX = 1027
FAVORITES = 1028

#
logger = getLogger(__name__)

class HeosClientProtocol():
    """
    Asynchronous protocol handler for Denon's Heos protocol for controlling home theatre receivers
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, host):
        self._host = host
        self._reader: StreamReader = None
        self._writer: StreamWriter = None
        self.system = _HeosSystem(self)
        self.browse = _HeosBrowse(self)
        self.group = _HeosGroup(self)
        self.players = {}

        self.inflight_commands = dict()
        self._sources = {}
        self._sequence = 1
        self._listeners = []
        self._progress_listeners = []
        self._players = []
        self._tasks = []

    def add_listener(self, listener):
        self._listeners += [listener]

    def add_progress_listener(self, listener):
        self._progress_listeners += [listener]

    async def setup(self):
        """
        Tasks we run as soon as the server is connected.  This includes turning on events,
        listing available music sources,  etc.

        In the immediate term I am working on a complete cycle of finding a piece of music
        and playing it and I am doing that here because it is easy,  probably if we want
        to separate this from the protocol,  this function can be implemented as a callback.

        :return:
        """
        (self._reader, self._writer) = await open_connection(self._host, HEOS_PORT)
        self._tasks.append(create_task(self.receive_loop()))
        await self.system.register_for_change_events()
        self._players = await _HeosPlayer(self).get_players()
        for player in self._players:
            self.players[player["name"]] = _HeosPlayer(self, player["pid"])

    async def shutdown(self):
        for task in self._tasks:
            task.cancel()

        for task in self._tasks:
            try:
                await task
            except CancelledError:
                pass

    async def receive_loop(self):
        while True:
            packet = await self._reader.readline()
            if packet:
                try:
                    jdata = json.loads(packet)
                    await self._handle_response(jdata)
                except JSONDecodeError:
                    logger.error("Error parsing %s  as json", jdata)
            else:
                break

    # pylint: disable=too-many-branches
    async def _handle_response(self, jdata):
        """
        Handles JSON response from server.  JSON responses can be produced in response to
        command as well as events that happen to the receiver.  Events are routed to the
        event handler,  while the system uses command names and sequence numbers to
        match commands with the futures that our clients are waiting on.

        :param jdata: a dict containing a parsed response Packet
        :return:
        """
        logger.debug(jdata)
        command = jdata["heos"]["command"]

        if command.startswith("event/"):
            event = command[command.index("/"):]
            if not "message" in jdata["heos"]:
                logger.debug("Got event of type [%s] with no message", event)
                message = {}
            else:
                message = {
                    key: value[0]
                    for key, value
                    in parse_qs(jdata["heos"]["message"]).items()
                }
            # pylint: disable=broad-except
            try:
                await self._handle_event(event, message)
            except Exception:
                logger.error("Caught exception while in event handler for %s",
                             event,
                             exc_info=True)
        else:
            try:
                if jdata["heos"]["message"].startswith("command under process"):
                    return

                message = {
                    key: value[0]
                    for key, value
                    in parse_qs(jdata["heos"]["message"]).items()
                }
            except KeyError:
                logger.error("Received HEOS reply for command %s without message", command)
                message = {}

            futures = self.inflight_commands[command]
            if "SEQUENCE" in message:
                sequence = int(message["SEQUENCE"])
                future = futures[sequence]
                logger.debug("Removing %s", future)
                del futures[sequence]
            elif len(futures) == 1:
                key = list(futures.keys())[0]
                future = futures[key]
                logger.debug("Removing %s", future)
                del futures[key]
            elif not futures:
                raise ValueError("No future found to match command: " + command)
            elif len(futures) > 1:
                raise ValueError("Multiple matching futures found for command: " + command)

            if not jdata["heos"]["result"] == "success":
                message = {key: value[0] for key, value in
                           parse_qs(jdata["heos"]["message"]).items()}
                future.set_exception(HeosError(message["eid"], message["text"]))
                return

            if message and "payload" in jdata:
                future.set_result(dict(message=message, payload=jdata["payload"]))
            elif message:
                future.set_result(message)
            elif "payload" in jdata:
                future.set_result(jdata["payload"])

            self.update_progress_listeners()

    # pylint: disable=no-self-use
    async def _handle_event(self, event, message):
        for listener in self._listeners:
            if iscoroutinefunction(listener):
                await listener(event, message)
            else:
                listener(event, message)

    def update_progress_listeners(self):
        count = 0
        for command in self.inflight_commands.values():
            count += len(command)
        for listener in self._progress_listeners:
            listener(count)

    def get_players(self):
        return self._players

    def __getitem__(self, that):
        for name, player in self.players.items():
            if that == name:
                return player
            if str(player.pid()) == str(that):
                return player
        raise KeyError(f"Couldn't find player with key {that}")


    def _run_command(self, command: str, **arguments) -> Future:
        future = create_future()
        this_event = self._sequence
        self._sequence += 1

        if not command in self.inflight_commands:
            self.inflight_commands[command] = {}
        self.inflight_commands[command][this_event] = future
        self.update_progress_listeners()

        base_url = f"heos://{command}"
        if arguments:
            if "SEQUENCE" not in arguments:
                arguments["SEQUENCE"] = this_event

            if not arguments["SEQUENCE"]:
                del arguments["SEQUENCE"]

        if arguments:
            url = base_url + "?" + "&".join(f"{key}={value}" for (key, value) in arguments.items())
        else:
            url = base_url

        logger.debug("Sending command %s", url)
        cmd = url + "\r\n"
        self._writer.write(cmd.encode("utf-8"))

        return future
