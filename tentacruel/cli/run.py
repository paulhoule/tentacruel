import asyncio
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

async def application(that:HeosClientProtocol):
    player = that[players[0]["pid"]]
    song = tracks[0]
    del song["key"]
    await player.add_to_queue(
        aid = 4,
        **song
    )

loop = asyncio.get_event_loop()
coro = loop.create_connection(
    lambda: HeosClientProtocol(loop,start_action=application),
    RECEIVER_IP, HEOS_PORT
)

loop.run_until_complete(coro)
loop.run_forever()
loop.close()