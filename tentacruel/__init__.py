# pylint: disable=missing-docstring
# pylint: disable=invalid-name

"""
Module to control Denon/Marantz
"""

import json
from collections import deque, defaultdict
from json import JSONDecodeError
from asyncio import create_task, open_connection, StreamReader, StreamWriter, iscoroutine, iscoroutinefunction
from asyncio import get_event_loop, Future, CancelledError
from typing import Dict, Set
from urllib.parse import parse_qs
from logging import getLogger
from uuid import uuid4

from tentacruel.service import _HeosService, HeosError
from tentacruel.system import _HeosSystem
from tentacruel.browse import _HeosBrowse
from tentacruel.player import _HeosPlayer
from tentacruel.group import _HeosGroup
from frozendict import frozendict

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

class MessageKeyGenerator():
    COMMANDS = {
        "browse/add_to_queue": ["SEQUENCE"],
        "group/get_groups": [],
        "group/set_group": ["pid"],
        "player/clear_queue": ["pid"],
        "player/get_players": [],
        "player/get_play_state": ["pid"],
        "player/set_play_state": ["pid"],
        "player/set_play_mode": ["pid", "repeat", "shuffle"],
        "player/set_volume": ["pid","level"],
        "system/register_for_change_events": []
    }

    def generate(self, command,  message):
        """
        Returns a hashable value that can be used as a dictionary key

        For the browse commands we append a random SEQUENCE
        identifier as a uuid,  otherwise we return a frozendict.

        :param command:
        :param message:
        :return:
        """
        if isinstance(message, str):
            message = {
                    key: value[0]
                    for key, value
                    in parse_qs(message).items()
                }

        hash = {"$command": command}
        for key in self.COMMANDS[command]:
            hash[key] = str(message[key])

        return frozendict(hash)


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

        self.inflight_commands = defaultdict(deque)
        self._sources = {}
        self._sequence = 1
        self._listeners = []
        self._progress_listeners = []
        self._players = []
        self._tasks = []
        self._keygen = MessageKeyGenerator()

    def add_listener(self, listener):
        self._listeners += [listener]

    def remove_listener(self, listener):
        self._listeners.remove(listener)

    def add_progress_listener(self, listener):
        self._progress_listeners += [listener]

    async def setup(self):
        """
        Tasks we run as soon as the server is connected.  This includes turning on events,
        listing available music sources,  etc.

        :return:
        """
        (self._reader, self._writer) = await open_connection(self._host, HEOS_PORT)
        self._tasks.append(await self.create_receive_loop())
        await self.system.register_for_change_events()
        self._players = await _HeosPlayer(self).get_players()
        for player in self._players:
            self.players[player["name"]] = _HeosPlayer(self, player["pid"])

    async def create_receive_loop(self):
        task = create_task(self.receive_loop())
        return task

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
            logger.debug("Waiting for message from HEOS server")
            packet = await self._reader.readline()
            logger.debug("HEOS server sent: %s", packet)
            if packet:
                try:
                    jdata = json.loads(packet)
                    await self._handle_response(jdata)
                except JSONDecodeError:
                    logger.error("Error parsing %s  as json", jdata)
            else:
                break
        logger.debug("Fell out of receive_loop");

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

            cmd_key = self._keygen.generate(command, message)
            future = self.inflight_commands[cmd_key].popleft()

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
        if command.startswith("browse/"):
            if "SEQUENCE" not in arguments:
                arguments["SEQUENCE"] = uuid4()

        cmd_key = self._keygen.generate(command, arguments)
        self.inflight_commands[cmd_key].append(future)
        self.update_progress_listeners()

        base_url = f"heos://{command}"
        if arguments:
            url = base_url + "?" + "&".join(f"{key}={value}" for (key, value) in arguments.items())
        else:
            url = base_url

        logger.debug("Sending command %s", url)
        cmd = url + "\r\n"
        self._writer.write(cmd.encode("utf-8"))

        return future
