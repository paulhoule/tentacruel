"""
Module to control Denon/Marantz
"""

import asyncio
import json
from json import JSONDecodeError
from urllib.parse import parse_qs
from logging import getLogger

from tentacruel.service import _HeosService
from tentacruel.system import _HeosSystem
from tentacruel.browse import _HeosBrowse
from tentacruel.player import _HeosPlayer

RECEIVER_IP = "192.168.0.10"
HEOS_PORT = 1255

LOCAL_MUSIC = 1024
PLAYLISTS = 1025
HISTORY = 1026
AUX = 1027
FAVORITES = 1028

logger = getLogger(__name__)

class HeosError(Exception):
    def __init__(self,error_id,message):
        super().__init__(f"Heos error {error_id}: {message}")
        self.error_id=error_id
        self.message=message

class HeosClientProtocol(asyncio.Protocol):
    """
    Asynchronous protocol handler for Denon's Heos protocol for controlling home theatre receivers
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, my_loop, start_action=None, halt=True):
        self._loop = my_loop
        self._start_action = start_action
        self._buffer = ""
        self._halt = halt

        self.system = _HeosSystem(self)
        self.browse = _HeosBrowse(self)
        self.players = {}

        self.inflight_commands = dict()
        self._sources = {}
        self._sequence = 1
        self._listeners = []
        self._progress_listeners = []

    def add_listener(self,listener):
        self._listeners += [listener]

    def add_progress_listener(self, listener):
        self._progress_listeners += [listener]

    def connection_made(self, transport):
        """
        Override method of Protocol called when connection is established.

        :param transport:
        :return:
        """
        self.transport = transport
        self._loop.create_task(self._setup())

    def data_received(self, data):
        """
        Override method of Protocol to handle incoming data.

        Collects incoming data in buffer,  breaks that data up into JSON packets which are
        delimited by '\r\n'.  Passes JSON packets into `_handle_response`

        :param data: available bytes
        :return:
        """
        self._buffer += data.decode()
        while True:
            try:
                index = self._buffer.index("\r\n")
            except ValueError:
                return

            packet = self._buffer[0:index]
            self._buffer = self._buffer[index + 2:]
            try:
                jdata = json.loads(packet)
                self._handle_response(jdata)
            except JSONDecodeError:
                logger.error("Error parsing %s  as json",jdata)

    def _handle_response(self, jdata):
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
            message = {key: value[0] for key, value in parse_qs(jdata["heos"]["message"]).items()}
            self._handle_event(event, message)
        else:
            if jdata["heos"]["message"].startswith("command under process"):
                return

            message = {key: value[0] for key, value in parse_qs(jdata["heos"]["message"]).items()}
            futures = self.inflight_commands[command]
            if "SEQUENCE" in message:
                sequence = int(message["SEQUENCE"])
                future = futures[sequence]
                logger.debug("Removing %s",future)
                del futures[sequence]
            elif len(futures) == 1:
                key = list(futures.keys())[0]
                future = futures[key]
                logger.debug("Removing %s",future)
                del futures[key]
            elif not futures:
                raise ValueError("No future found to match command: " + command)
            elif len(futures) > 1:
                raise ValueError("Multiple matching futures found for command: " + command)

            if not jdata["heos"]["result"] == "success":
                message = {key: value[0] for key, value in
                           parse_qs(jdata["heos"]["message"]).items()}
                future.set_exception(HeosError(message["eid"],message["text"]))
                return

            payload = jdata.get("payload")
            if message and payload:
                future.set_result(dict(message=message, payload=payload))
            elif message:
                future.set_result(message)
            elif payload:
                future.set_result(payload)

            self.update_progress_listeners()

    # pylint: disable=no-self-use
    def _handle_event(self, event, message):
        for listener in self._listeners:
            listener(event,message)

    def update_progress_listeners(self):
        count = 0
        for command in self.inflight_commands.values():
            count += len (command)
        for listener in self._progress_listeners:
            listener(count)


    def connection_lost(self, exc):
        self._loop.stop()

    async def _setup(self):
        """
        Tasks we run as soon as the server is connected.  This includes turning on events,
        listing available music sources,  etc.

        In the immediate term I am working on a complete cycle of finding a piece of music
        and playing it and I am doing that here because it is easy,  probably if we want
        to separate this from the protocol,  this function can be implemented as a callback.

        :return:
        """
        await self.system.register_for_change_events()
        self._players = await _HeosPlayer(self).get_players()
        for player in self._players:
            self.players[player["name"]]=_HeosPlayer(self,player["pid"])

        if self._start_action:
            await self._start_action(self)

        if self._halt:
            self._loop.stop()

    def get_players(self):
        return self._players

    def __getitem__(self,that):
        for name,player in self.players.items():
            if that==name:
                return player
            if str(player._player_id) == str(that):
                return player
        raise KeyError(f"Couldn't find player with key {that}")


    def _run_command(self, command: str, arguments: dict = {}) -> asyncio.Future:
        future = self._loop.create_future()
        this_event = self._sequence
        self._sequence += 1

        if not command in self.inflight_commands:
            self.inflight_commands[command] = {}
        self.inflight_commands[command][this_event] = future
        self.update_progress_listeners()

        base_url = f"heos://{command}"
        if arguments:
            arguments["SEQUENCE"]=this_event

        if arguments:
            url = base_url + "?" + "&".join(f"{key}={value}" for (key,value) in arguments.items())
        else:
            url = base_url

        logger.debug("Sending command %s", url)
        cmd = url + "\r\n"
        self.transport.write(cmd.encode("utf-8"))

        return future


