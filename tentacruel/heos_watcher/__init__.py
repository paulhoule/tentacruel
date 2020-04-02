from uuid import UUID

from aio_pika import Exchange
from tentacruel import HeosClientProtocol

HEOS_NS = UUID('003df636-ad90-11e9-aca1-9eb6d06a70c5')
attributes = {
    "/player_volume_changed": {
        "device_id": "pid",
        "name": "heos.volume",
        "subattributes": ["level", "mute"]
    },
    "/player_now_playing_progress": {
        "device_id": "pid",
        "name": "heos.progress",
        "subattributes": ["cur_pos", "duration"]
    }
}

class HeosWatcher:

    def __init__(self, config, exchange: Exchange):
        self.config = config
        self.exchange = exchange

    async def setup(self):
        self._heos = HeosClientProtocol(self.config["server"]["ip"])
        await self._heos.setup()
        self._heos.add_listener(self.listener)

    async def run(self):
        await self.setup()

    async def listener(self, event, message):
        print(event)
        print(message)
        print("--------------")
