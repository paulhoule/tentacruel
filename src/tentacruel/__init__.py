import asyncio
from asyncio import Future
import json
import sys
from json import JSONDecodeError
from urllib.parse import parse_qs, urlencode

from tentacruel.service import _HeosService
from tentacruel.system import _HeosSystem
from tentacruel.browse import _HeosBrowse
from tentacruel.player import _HeosPlayer

receiver_ip = "192.168.0.10"
heos_port = 1255

LOCAL_MUSIC = 1024
PLAYLISTS = 1025
HISTORY = 1026
AUX = 1027
FAVORITES = 1028

class HeosClientProtocol(asyncio.Protocol):
    """
    Asynchronous protocol handler for Denon's Heos protocol for controlling home theatre receivers
    """

    def __init__(self,loop):
        self._loop = loop
        self._buffer = ""
        self.system = _HeosSystem(self)
        self.browse = _HeosBrowse(self)
        self.player = _HeosPlayer(self)

        self.inflight_commands = dict()
        self._sources = {}
        self._sequence = 1

    def connection_made(self,transport):
        """
        Override method of Protocol called when connection is established.

        :param transport:
        :return:
        """
        self.transport = transport
        self._loop.create_task(self._setup())

    def data_received(self,data):
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
                print("Error parsing "+jdata+" as json")

    def _handle_response(self, jdata):
        """
        Handles JSON response from server.  JSON responses can be produced in response to
        command as well as events that happen to the receiver.  Events are routed to the
        event handler,  while the system uses command names and sequence numbers to
        match commands with the futures that our clients are waiting on.

        :param jdata: a dict containing a parsed response Packet
        :return:
        """
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
                del futures[sequence]
            elif len(futures) == 1:
                key = list(futures.keys())[0]
                future = futures[key]
                del futures[key]
            elif len(futures) == 0:
                raise ValueError("No future found to match command: "+command)
            elif len(futures) > 1:
                raise ValueError("Multiple matching futures found for command: "+command)

            if not jdata["heos"]["result"] == "success":
                future.set_exception(Exception("Error processing HEOS command",jdata))
                return

            payload = jdata.get("payload")
            if message and payload:
                future.set_result(dict(message=message,payload=payload))
            elif message:
                future.set_result(message)
            elif payload:
                future.set_result(payload)

    def _handle_event(self, event, message):
        print("Got event"+event)
        print(message)

    def connection_lost(self,exc):
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
        self._players = await self.player.get_players()
        self._player_id = self._players[0]['pid']
        await self.player.set_play_state("play")
        await self.player.remove_from_queue(range(30,70))
        print(await self.player.get_queue())
        return

        sources = await self.browse.get_music_sources()
        self._sources = {source["sid"]:source for source in sources if source["available"]=="true"}


        local_sources = (await self.browse.browse(LOCAL_MUSIC))["payload"]
        looking_for = "Plex Media Server: tamamo"
        ok_sources = [source for source in local_sources if source["name"] == looking_for]
        sid = ok_sources[0]["sid"]
        r2 = await self.browse.browse_for_name(["Music","Music","By Album","Thomas Dolby - Aliens Ate My Buick (1988)"],sid)
        r3 = await self.browse.browse(sid,r2["cid"])


        #print(r3)



    def _run_command(self, command:str, arguments:dict={}) -> asyncio.Future:
        future = self._loop.create_future()
        this_event = self._sequence
        self._sequence += 1

        if not command in self.inflight_commands:
            self.inflight_commands[command] = {}
        self.inflight_commands[command][this_event] = future

        base_url = f"heos://{command}"
#        if arguments:
#            arguments["SEQUENCE"]=this_event

        if arguments:
            url = base_url + "?" + urlencode(arguments)
        else:
            url = base_url

        print("Sending command "+url)
        cmd = url + "\r\n"
        self.transport.write(cmd.encode("utf-8"))

        return future



loop = asyncio.get_event_loop()
coro = loop.create_connection(
    lambda: HeosClientProtocol(loop),
    receiver_ip, heos_port
)

loop.run_until_complete(coro)
loop.run_forever()
loop.close()
