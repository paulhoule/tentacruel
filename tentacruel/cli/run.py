# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import asyncio
import datetime
import json
import re
import sys
from logging import getLogger, StreamHandler
from os import environ
from pathlib import Path

import yaml
from arango import DocumentGetError
from tentacruel import HeosClientProtocol, _HeosPlayer, keep
from tentacruel.cli.control_lights import ControlLights
from tentacruel.cli.lights import LightCommands
from tentacruel.cli.drain_sqs import DrainSQS

logger = getLogger(__name__)
if "LOGGING_LEVEL" in environ:
    getLogger(None).setLevel(environ["LOGGING_LEVEL"])

getLogger(None).addHandler(StreamHandler())

with open(Path.home() / ".tentacruel" / "config.yaml") as a_stream:
    config = yaml.load(a_stream)

RECEIVER_IP = config["server"]["ip"]
players = config["players"]

def separate_commands(arguments):
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

# pylint: disable=too-many-locals
def sun_time(which_one="sunrise"):
    from skyfield import api, almanac
    import dateutil.tz
    load = api.Loader("~/.skyfield", verbose=False)
    location = config["location"]
    ts = load.timescale()
    e = load('de421.bsp')
    here = api.Topos(location["latitude"], location["longitude"])
    now = datetime.datetime.now()
    today = now.date()
    local = dateutil.tz.gettz()
    midnight = datetime.datetime.combine(today, datetime.time(), local)
    next_midnight = midnight + datetime.timedelta(1)
    begin = ts.utc(midnight)
    end = ts.utc(next_midnight)
    t, _ = almanac.find_discrete(begin, end, almanac.sunrise_sunset(e, here))
    idx = 0 if which_one == "sunrise" else 1
    return t[idx].astimezone(local)

# pylint: disable=too-few-public-methods
class Application:
    def __init__(self, argv):
        self.argv = argv
        self.commands = Application.Commands(self)


    # pylint: disable=too-many-instance-attributes
    class Commands:
        def __init__(self, parent):
            self.parent = parent
            self._player: _HeosPlayer = None
            self._lights = LightCommands(parent)
            self._sensor_states = {}
            self._off_at = None
            self._prefixes = {"list"}
            self._heos_client = None

        async def _heos(self):
            if not self._heos_client:
                self._heos_client = HeosClientProtocol(config["server"]["ip"])
                await self._heos_client.setup()

            return self._heos_client

        async def light(self, parameters):
            await self._lights.do(parameters)

        async def drain_sqs(self, parameters):
            queue = DrainSQS(config)
            await queue.do(parameters)

        async def control_lights(self, parameters):
            control = ControlLights(config)
            await control.do(parameters)

        async def player(self, parameters):
            if len(parameters) != 1:
                raise ValueError("The player command takes exactly one argument,"
                                 "  the number or name of the player")

            player_specification = parameters[0]
            pid = self._parse_player_specification(player_specification)

            heos = await self._heos()
            self._player = heos[pid]

        # pylint: disable=no-self-use
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
                    "You much specify a numeric player id or player key"
                    " registered in the configuration file")
            return pid

        async def play(self, parameters):
            if not parameters:
                await self._player.set_play_state("play")
            else:
                await self._player.clear_queue()

                for track in parameters:
                    aid = _HeosPlayer.REPLACE_AND_PLAY
                    song = await self._search_local_tracks(track)
                    if not song:
                        song = await self._search_network_tracks(track)
                    if not song:
                        raise ValueError(f"Could not find track named '{track}'")
                    song = keep(song, {"cid", "sid", "mid"})
                    await self._player.add_to_queue(aid=aid, **song)

                await self._player.set_play_mode()

        async def _search_local_tracks(self, track):
            if "tracks" in config:
                for entry in config["tracks"]:
                    if entry["key"] == track:
                        return dict(entry)

        async def _search_network_tracks(self, track):
            adb = self._connect_to_adb()
            collection = adb.collection("tracks")
            try:
                return collection.get(track)
            except DocumentGetError:
                return None

        async def stop(self, parameters):
            if parameters:
                raise ValueError("The stop command takes no arguments")

            await self._player.set_play_state("stop")

        async def pause(self, parameters):
            if parameters:
                raise ValueError("The pause command takes no arguments")

            await self._player.set_play_state("pause")

        async def mute(self, parameters):
            if parameters:
                raise ValueError("The mute command takes no arguments")

            await self._player.set_mute("on")

        async def unmute(self, parameters):
            if parameters:
                raise ValueError("The mute command takes no arguments")

            await self._player.set_mute("off")

        async def volume(self, parameters):
            if len(parameters) != 1:
                raise ValueError("The volume command takes exactly one parameter")

            volume = float(parameters[0])
            if volume < 0.0 or volume > 100.0:
                raise ValueError("The volume parameter must be between 0.0 and 100.0")

            await self._player.set_volume(volume)

        async def list_groups(self, parameters):
            if parameters:
                raise ValueError("The list groups command takes no arguments")

            heos = await self._heos()
            result = await heos.group.get_groups()
            if not result:
                print(f"The HEOS system has no groups.")
            idx = 1
            for group in result:
                print(f"Group {idx}:")
                print(f"   Name: {group['name']}")
                print(f"   Gid: {group['gid']}")
                print(f"   Players:")
                for player in group["players"]:
                    print(f"      {player['role']} {player['name']} ({player['pid']})")
                idx += 1

        async def ungroup(self, parameters):
            if parameters:
                raise ValueError("The clear_groups command takes no arguments")

            heos = await self._heos()
            result = await heos.group.get_groups()
            for group in result:
                leader = [
                    player["pid"]
                    for player in group["players"]
                    if player["role"] == "leader"
                ]
                await heos.group.set_group(leader)

        async def group(self, parameters):
            if not parameters:
                raise ValueError("You must specify multiple player names to create a group")

            heos = await self._heos()
            if parameters == ['all']:
                pid_list = [player.pid() for player in heos.players.values()]
            else:
                pid_list = [self._parse_player_specification(x) for x in parameters]
            await heos.group.set_group(pid_list)

        # pylint: disable=too-many-branches
        async def wait(self, parameters):
            if not parameters:
                raise ValueError("You must specify a time to wait")

            # The syntax is getting complex enough here that there should be tests (also a plan
            # to parse).  I am trying to fake english here::
            #
            #     wait until 4:00 pm
            #
            #

            if parameters[0] == "until":
                if parameters[-1] in {"sunrise", "sunset"}:
                    event = sun_time(parameters[-1])
                    if len(parameters) == 5:
                        amount = int(parameters[1])
                        unit = parameters[2]
                        direction = parameters[3]
                        if direction not in {"before", "after"}:
                            raise ValueError("A time must be specified before or"
                                             " after sunset or sunrise")
                        amount = self._convert_to_seconds(amount, unit)
                        if direction == "before":
                            amount = -amount
                        event += datetime.timedelta(seconds=amount)
                    elif len(parameters) == 2:
                        pass
                    else:
                        raise ValueError("syntax: wait until 5 minutes before sunrise")
                    import dateutil.tz
                    delay = (event - datetime.datetime.now(tz=dateutil.tz.gettz())).total_seconds()
                    logger.debug("Waiting for %d seconds", delay)
                    return await asyncio.sleep(delay)

                if len(parameters) == 1:
                    raise ValueError("You must specify a time to wait until")

                when = parameters[1]
                match = re.match(r"(\d{1,2}):(\d{2})(:\d{2})?", when)
                if match:
                    hours = int(match.group(1))
                    minutes = int(match.group(2))
                    seconds = int(match.group(3)[1:]) if match.group(3) else 0
                    now = datetime.datetime.now()
                    current_date = now.date()
                    current_time = now.time()
                    that_time = datetime.time(hours, minutes, seconds)
                    if that_time < current_time:
                        current_date += datetime.timedelta(1)
                    target_time = datetime.datetime.combine(current_date, that_time)
                    delay = (target_time - now).total_seconds()
                    logger.debug("Waiting for %d seconds", delay)
                    return await asyncio.sleep(delay)

            if re.match(r"\d+", parameters[0]):
                duration = int(parameters[0])
                if len(parameters) > 2:
                    raise ValueError("You can at most specify a numeric duration and a unit")

                if len(parameters) == 2:
                    duration = self._convert_to_seconds(duration, parameters[1])

                return await asyncio.sleep(duration)

            raise ValueError("You must specify a numeric amount of time to wait")

        def _convert_to_seconds(self, duration, unit):
            if unit in {"s", "sec", "seconds", "second"}:
                pass
            elif unit in {"m", "min", "minutes", "minute"}:
                duration *= 60
            elif unit in {"h", "hr", "hrs", "hour", "hours"}:
                duration *= 3600
            else:
                raise ValueError("permissible units are seconds,  minutes,  and hours")
            return duration

        async def defend(self, parameters):
            if parameters:
                raise ValueError("defend command takes no parameters")

            light_zones = [
                ("Bedroom", "Bedroom", "TurnOnBedroom", "ThankYou"),
                ("Hallway", "Room23", "TurnOnHallway", "ThankYou"),
                ("Bottom of Stairs", "Kitchen", "TurnOnDownstairs", "ThankYou")
            ]

            for zone in light_zones:
                lights_ok = await self.enforce_lights(*zone)
                if not lights_ok:
                    break

        async def enforce_lights(self, group, player, request_voice, thankyou_voice):
            # pylint: disable=protected-access
            lights = self._lights._get_unreachable_lights(group)
            if not lights:
                return True

            await self.player([player]) # Not the same bedroom
            await self.play([request_voice])

            for _ in range(0, 200):
                await asyncio.sleep(1)
                lights = self._lights._get_unreachable_lights(group)
                if not lights:
                    await self.play([thankyou_voice])
                    group_id = self._lights._bridge.get_group_id_by_name(group)
                    self._lights._bridge.set_group(group_id, "on", False)
                    return False

        def _connect_to_adb(self):
            from arango import ArangoClient
            client = ArangoClient(**config["arangodb"]["events"]["client"])
            return client.db(**config["arangodb"]["events"]["database"])

        async def load_tracks(self, parameters):
            if parameters:
                raise ValueError("load_tracks takes no parameters")

            adb = self._connect_to_adb()
            collection = adb.collection("tracks")
            for track in config["tracks"]:
                track["_key"] = track["key"]
                del track["key"]
                collection.insert(track)

        async def read_smartthings_configuration(self, parameters):
            if parameters:
                raise ValueError("read_smartthings_configuration takes no parameters")
            adb = self._connect_to_adb()
            collection = adb.collection("devices")
            import requests
            access_token = config["smartthings"]["personal_access_token"]
            headers = {
                "Authorization": f"Bearer {access_token}"
            }

            url = f"https://api.smartthings.com/devices"
            while url:
                response = requests.get(url, headers=headers)
                device_batch = []
                device_info = json.loads(response.content)
                for item in device_info["items"]:
                    device = dict(item)
                    device["_key"] = device["deviceId"]
                    del device["deviceId"]
                    device_batch.append(device)
                collection.insert_many(device_batch, overwrite=True)
                if "next" in device_info["_links"]:
                    url = device_info["_links"]["next"]["href"]
                else:
                    url = None

    async def run(self):
        if len(self.argv) == 1:
            self.help()

        commands = separate_commands(self.argv[1:])
        for command in commands:
            command_name = command[0]
            idx = 1
            # pylint: disable=protected-access
            if command_name in self.commands._prefixes:
                command_name = f"{command_name}_{command[1]}"
                idx += 1
            command_action = getattr(self.commands, command_name)
            await command_action(command[idx:])

    def help(self):
        """
        Please enter the correct command string

        :return:
        """
        help(self.help)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    application = Application(sys.argv)
    loop.run_until_complete(application.run())
    loop.close()
