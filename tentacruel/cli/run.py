import asyncio
import datetime
import json
import re
import sys
from logging import getLogger, StreamHandler
from os import environ
from pathlib import Path

import yaml
from phue import Bridge
from tentacruel import HeosClientProtocol, HEOS_PORT

logger = getLogger(__name__)
if "LOGGING_LEVEL" in environ:
    getLogger(None).setLevel(environ["LOGGING_LEVEL"])

getLogger(None).addHandler(StreamHandler())

with open(Path.home() / ".tentacruel" / "config.yaml") as that:
    config = yaml.load(that)

RECEIVER_IP = config["server"]["ip"]
players = config["players"]
tracks = config["tracks"]

def sun_time(which_one="sunrise"):
    from skyfield import api,almanac
    import dateutil.tz
    load = api.Loader("~/.skyfield",verbose=False)
    location = config["location"]
    ts = load.timescale()
    e = load('de421.bsp')
    here = api.Topos(location["latitude"],location["longitude"])
    now = datetime.datetime.now()
    today = now.date()
    local = dateutil.tz.gettz()
    midnight=datetime.datetime.combine(today,datetime.time(),local)
    next_midnight = midnight + datetime.timedelta(1)
    begin = ts.utc(midnight)
    end = ts.utc(next_midnight)
    t, y = almanac.find_discrete(begin, end, almanac.sunrise_sunset(e, here))
    idx = 0 if which_one=="sunrise" else 1
    return t[idx].astimezone(local)



class Application:
    def __init__(self,argv):
        self.argv = argv
        self.commands = Application.Commands(self)

    class LightCommands:
        #
        # only numeric for now
        #
        attributes = {
            "transitiontime",
            "brightness",
            "colortemp",
            "colortemp_k",
            "hue",
            "saturation"
        }
        def __init__(self, parent):
            self.parent = parent
            self._bridge = Bridge()

        def do(self, parameters):
            idx = 0
            first = parameters[idx]
            idx += 1
            pattern = re.compile("[0-9]+")
            if pattern.match(first):
                light_id = int(first)
                light = self._bridge.lights[light_id - 1]
            elif first == "group":
                second = parameters[idx]
                idx +=1
                group_id = int(second)
                light = self._bridge.groups[group_id - 1]
            else:
                raise ValueError("the light command must be followed by a number or by 'group' and then a number")

            while idx<len(parameters):
                cmd = parameters[idx]
                idx += 1
                if cmd == "on":
                    light.on = True
                elif cmd == "off":
                    light.on = False
                elif cmd in Application.LightCommands.attributes:
                    amount = int(parameters[idx])
                    idx += 1
                    setattr(light,cmd,amount)
                else:
                    raise ValueError(f"Command {cmd} is not available for lights")

        def _get_unreachable_lights(self,group_name):
            that = self._bridge.get_group(group_name)
            not_available = set()
            for light in map(int, that['lights']):
                if not self._bridge.get_light(light)['state']['reachable']:
                    not_available.add(light)
            return not_available

    class Commands:
        def __init__(self,parent):
            self.parent = parent
            self._player = None
            self._lights = Application.LightCommands(parent)
            self._prefixes = {"list"}

        def _heos(self):
            return self.parent._heos

        async def light(self, parameters):
            self._lights.do(parameters)

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

        async def list_groups(self,parameters):
            if len(parameters):
                raise ValueError("The list groups command takes no arguments")

            result = await self._heos().group.get_groups()
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

            if parameters == ['all']:
                pid_list = [player.pid() for player in self._heos().players.values()]
            else:
                pid_list = [self._parse_player_specification(x) for x in parameters]
            await self._heos().group.set_group(pid_list)

        async def wait(self,parameters):
            if not len(parameters):
                raise ValueError("You must specify a time to wait")

            """
            The syntax is getting complex enough here that there should be tests (also a plan
            to parse).  I am trying to fake english here::
            
                wait until 4:00 pm
                
            """
            if parameters[0]=="until":
                if parameters[-1] in {"sunrise","sunset"}:
                    event = sun_time(parameters[-1])
                    if len(parameters)==5:
                        amount = int(parameters[1])
                        unit = parameters[2]
                        direction = parameters[3]
                        if direction not in {"before","after"}:
                            raise ValueError("A time must be specified before or after sunset or sunrise")
                        amount = self._convert_to_seconds(amount,unit)
                        if direction == "before":
                            amount = -amount
                        event +=  datetime.timedelta(seconds=amount)
                    elif len(parameters)==2:
                        pass
                    else:
                        raise ValueError("syntax: wait until 5 minutes before sunrise")
                    import dateutil.tz
                    delay = (event - datetime.datetime.now(tz=dateutil.tz.gettz())).total_seconds()
                    logger.debug("Waiting for %d seconds",delay)
                    return await asyncio.sleep(delay)

                if len(parameters)==1:
                    raise ValueError("You must specify a time to wait until")

                when = parameters[1]
                match = re.match("(\d{1,2}):(\d{2})(:\d{2})?",when)
                if match:
                    hours = int(match.group(1))
                    minutes = int(match.group(2))
                    seconds = int(match.group(3)[1:]) if match.group(3) else 0
                    now = datetime.datetime.now()
                    current_date = now.date()
                    current_time = now.time()
                    that_time = datetime.time(hours,minutes,seconds)
                    if that_time<current_time:
                        current_date += datetime.timedelta(1)
                    target_time = datetime.datetime.combine(current_date,that_time)
                    delay = (target_time - now).total_seconds()
                    logger.debug("Waiting for %d seconds",delay)
                    return await asyncio.sleep(delay)

            if re.match("\d+",parameters[0]):
                duration = int(parameters[0])
                if len(parameters)>2:
                    raise ValueError("You can at most specify a numeric duration and a unit")

                if len(parameters)==2:
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

        async def defend(self,parameters):
            lights = self._lights._get_unreachable_lights("Bedroom")
            if lights:
                await self.player(["Bedroom"]) # Not the same bedroom\
                await self.play([("IvyTurnOnBedroom")])

                for _ in range(0,200):
                    await asyncio.sleep(1)
                    lights = self._lights._get_unreachable_lights("Bedroom")
                    if not lights:
                        await self.play(["IvyThankYou"])
                        group_id = self._lights._bridge.get_group_id_by_name("Bedroom")
                        self._lights._bridge.set_group(group_id,"on",False)
                        return

        async def process_sensor_events(self,parameters):
            from arango import ArangoClient
            client=ArangoClient(**config["arangodb"]["events"]["client"])
            adb = client.db(**config["arangodb"]["events"]["database"])
            collection = adb.collection("sqs_events")
            import boto3
            sqs = boto3.client(
                    "sqs",
                    aws_access_key_id=config["aws"]["aws_access_key_id"],
                    aws_secret_access_key=config["aws"]["aws_secret_access_key"],
                    region_name=config["aws"]["region_name"])
            error_count = 0
            while(True):
                try:
                    events = await self._poll_sqs(collection, sqs)
                    error_count = 0
                except Exception as ex:
                    logger.error(ex)
                    error_count += 1
                    if error_count>1:
                        logger.error("%d consecutive errors polling from SQS queue",error_count)

                    await asyncio.sleep(10)
                    continue

        async def _poll_sqs(self, collection, sqs):
            response = sqs.receive_message(
                QueueUrl=config["aws"]["queue_url"],
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20
            )
            event_batch = []
            delete_batch = []
            if "Messages" not in response:
                if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                    logger.error("Got error while receiving queue messages; response: %s", response)
                    return []
            else:
                for message in response["Messages"]:
                    delete_batch.append({
                        "Id": message["MessageId"],
                        "ReceiptHandle": message["ReceiptHandle"]
                    })
                    body = json.loads(message["Body"])
                    for event in body:
                        device_event = dict(event["deviceEvent"])
                        device_event["_key"] = device_event["eventId"]
                        device_event["eventTime"] = event["eventTime"]
                        del (device_event["eventId"])
                        event_batch.append(device_event)

                collection.insert_many(event_batch)
                sqs.delete_message_batch(
                    QueueUrl=config["aws"]["queue_url"],
                    Entries=delete_batch
                )




    async def run(self,that:HeosClientProtocol):
        self._heos = that
        if len(self.argv)==1:
            self.help()

        commands = self.separate_commands(self.argv[1:])
        for command in commands:
            command_name = command[0]
            idx = 1
            if command_name in self.commands._prefixes:
                command_name = f"{command_name}_{command[1]}"
                idx += 1
            command_action = getattr(self.commands,command_name)
            await command_action(command[idx:])

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