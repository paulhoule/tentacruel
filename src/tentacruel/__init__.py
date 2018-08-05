import asyncio
import json
import sys
from json import JSONDecodeError
from urllib.parse import parse_qs, urlencode

receiver_ip = "192.168.0.10"
heos_port = 1255

class _HeosSystem():
    def __init__(self,protocol):
        self.protocol=protocol

    async def register_for_change_events(self,enable=True) -> asyncio.Future:
        future = self.protocol.run_command(
            "system/register_for_change_events",
            dict(enable = "on" if enable else "off")
        )

        result = await future


class _HeosBrowse():
    def __init__(self,protocol):
        self.protocol=protocol

    async def get_music_sources(self) -> asyncio.Future:
        future = self.protocol.run_command("browse/get_music_sources")
        result = await future
        print(result)

class HeosClientProtocol(asyncio.Protocol):
    def __init__(self,loop):
        self.loop = loop
        self.buffer = ""
        self.system = _HeosSystem(self)
        self.browse = _HeosBrowse(self)
        self.inflight_commands = dict()

    def connection_made(self,transport):
        self.transport = transport
        self.loop.create_task(self.setup())

    def data_received(self,data):
        self.buffer += data.decode()
        while True:
            try:
                index = self.buffer.index("\r\n")
            except ValueError:
                return

            packet = self.buffer[0:index]
            self.buffer = self.buffer[index+2:]
            try:
                jdata = json.loads(packet)
                self.handle_response(jdata)
            except JSONDecodeError:
                print("Error parsing "+jdata+" as json")


    def handle_response(self,jdata):
        command = jdata["heos"]["command"]
        if command.startswith("event/"):
            event = command[command.index("/"):]
            message = {key: value[0] for key, value in parse_qs(jdata["heos"]["message"]).items()}
            self.handle_event(event,message)
        else:
            future:asyncio.Future = self.inflight_commands[command]
            del self.inflight_commands[command]
            if not jdata["heos"]["result"] == "success":
                future.set_exception(Exception("Error processing HEOS command",jdata))
            else:
                if jdata["heos"]["message"]:
                    result={key: value[0] for key, value in parse_qs(jdata["heos"]["message"]).items()}
                else:
                    result=jdata["payload"]
                future.set_result(result)

    def handle_event(self,event,message):
        print("Got event"+event)
        print(message)

    def connection_lost(self,exc):
        self.loop.stop()

    async def setup(self):
        await self.system.register_for_change_events()

    def run_command(self,command:str ,arguments:dict={}) -> asyncio.Future:
        base_url = f"heos://{command}"
        if arguments:
            url = base_url + "?" + urlencode(arguments)
        else:
            url = base_url

        cmd = url + "\r\n"
        print(cmd)
        self.transport.write(cmd.encode("utf-8"))
        future = self.loop.create_future()
        self.inflight_commands[command] = future
        return future



loop = asyncio.get_event_loop()
coro = loop.create_connection(
    lambda: HeosClientProtocol(loop),
    receiver_ip, heos_port
)

loop.run_until_complete(coro)
loop.run_forever()
loop.close()
