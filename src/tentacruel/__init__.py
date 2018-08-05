import asyncio
import json
import sys
from json import JSONDecodeError
from urllib.parse import parse_qs

receiver_ip = "192.168.0.10"
heos_port = 1255

class HeosClientProtocol(asyncio.Protocol):
    def __init__(self,loop):
        self.loop = loop
        self.buffer = ""

    def connection_made(self,transport):
        self.transport = transport
        self.transport.write(b"heos://system/register_for_change_events?enable=on\r\n")

    def data_received(self,data):
        self.buffer += data.decode()
        while True:
            try:
                index = self.buffer.index("\r\n")
            except ValueError:
                return

            packet = self.buffer[0:index]
            print(len(packet))
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

        print("Got command response")

    def handle_event(self,event,message):
        print("Got event"+event)
        print(message)

    def connection_lost(self,exc):
        self.loop.stop()

loop = asyncio.get_event_loop()
coro = loop.create_connection(
    lambda: HeosClientProtocol(loop),
    receiver_ip, heos_port
)

loop.run_until_complete(coro)
loop.run_forever()
loop.close()
