import asyncio
import re
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
            self._player = None

        def _heos(self):
            return self.parent._heos

        async def player(self, parameters):
            if len(parameters) != 1:
                raise ValueError("The player command takes exactly one argument,  the number or name of the player")

            player_specification = parameters[0]
            pid = self._parse_player_specification(player_specification)

            self._player = self._heos()[pid]

        def _parse_player_specification(self, player_specification):
            pid = None
            try:
                pid = int(player_specification)
            except ValueError:
                for player in players:
                    if player["key"] == player_specification:
                        pid = player["pid"]
                        break
            if not pid:
                raise ValueError(
                    "You much specify a numeric player id or player key registered in the configuration file")
            return pid

        async def play(self,parameters):
            if not len(parameters):
                await self._player.set_play_state("play")
            else:
                aid = 4
                for track in parameters:
                    for entry in tracks:
                        if entry["key"] == track:
                            song = dict(entry)
                            del song["key"]
                            await self._player.add_to_queue(aid=aid,**song)
                            aid=3

        async def stop(self,parameters):
            if len(parameters):
                raise ValueError("The stop command takes no arguments")

            await self._player.set_play_state("stop")

        async def pause(self,parameters):
            if len(parameters):
                raise ValueError("The pause command takes no arguments")

            await self._player.set_play_state("pause")

        async def mute(self,parameters):
            if len(parameters):
                raise ValueError("The mute command takes no arguments")

            await self._player.set_mute("on")

        async def unmute(self,parameters):
            if len(parameters):
                raise ValueError("The mute command takes no arguments")

            await self._player.set_mute("off")

        async def volume(self,parameters):
            if len(parameters) != 1:
                raise ValueError("The volume command takes exactly one parameter")

            volume = float(parameters[0])
            if volume<0.0 or volume>100.0:
                raise ValueError("The volume parameter must be between 0.0 and 100.0")

            await self._player.set_volume(volume)

        async def get_groups(self,parameters):
            if len(parameters):
                raise ValueError("The get_groups command takes no arguments")

            result = await self._heos().group.get_groups()
            print("Got back from get_groups")
            print(result)

        async def ungroup(self,parameters):
            if len(parameters):
                raise ValueError("The clear_groups command takes no arguments")

            result = await self._heos().group.get_groups()
            for group in result:
                leader = [player["pid"] for player in group["players"] if player["role"] == "leader"]
                await self._heos().group.set_group(leader)

        async def group(self,parameters):
            if not len(parameters):
                raise ValueError("You must specify multiple player names to create a group")

            pid_list = [self._parse_player_specification(x) for x in parameters]
            await self._heos().group.set_group(pid_list)

    async def run(self,that:HeosClientProtocol):
        self._heos = that
        if len(self.argv)==1:
            self.help()

        commands = self.separate_commands(self.argv[1:])
        for command in commands:
            command_name = command[0]
            command_action = getattr(self.commands,command_name)
            await command_action(command[1:])

    def separate_commands(self,arguments):
        commands = []
        current_command = []
        divider_pattern = re.compile(r"\\+")
        for argument in arguments:
            if divider_pattern.fullmatch(argument):
                commands.append(current_command)
                current_command = []
            else:
                current_command.append(argument)
        if current_command:
            commands.append(current_command)
        return commands

    def help(self):
        """
        Please enter the correct command string

        :return:
        """
        help(self.help)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    application=Application(sys.argv)

    coro = loop.create_connection(
        lambda: HeosClientProtocol(loop,start_action=application.run),
        RECEIVER_IP, HEOS_PORT
    )

    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()