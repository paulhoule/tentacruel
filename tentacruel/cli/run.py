import asyncio
import sys
from logging import getLogger, StreamHandler
from os import environ
from pathlib import Path

import yaml
from tentacruel import HeosClientProtocol, HEOS_PORT

logger = getLogger(__name__)
if "LOGGING_LEVEL" in environ:
    getLogger(None).setLevel(environ["LOGGING_LEVEL"])

getLogger(None).addHandler(StreamHandler())

with open(Path.home() / ".tentacruel" / "config.yaml") as config:
    parameters = yaml.load(config)

RECEIVER_IP = parameters["server"]["ip"]
players = parameters["players"]
tracks = parameters["tracks"]

class Application:
    def __init__(self,argv):
        self.argv = argv
        self.commands = Application.Commands(self)

    class Commands:
        def __init__(self,parent):
            self.parent = parent

        def that(self):
            return self.parent.that

        async def play(self):
            player = self.that()[players[0]["pid"]]
            await player.set_play_state("play")

        async def stop(self):
            player = self.that()[players[0]["pid"]]
            await player.set_play_state("stop")


    async def run(self,that:HeosClientProtocol):
        self.that = that
        if len(self.argv)==1:
            self.help()

        command_name = self.argv[1]
        command_action = getattr(self.commands,command_name)
        await command_action()

    def help(self):
        """
        Please enter the correct command string

        :return:
        """
        help(self.help)

loop = asyncio.get_event_loop()
application=Application(sys.argv)

coro = loop.create_connection(
    lambda: HeosClientProtocol(loop,start_action=application.run),
    RECEIVER_IP, HEOS_PORT
)

loop.run_until_complete(coro)
loop.run_forever()
loop.close()