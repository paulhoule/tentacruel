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
