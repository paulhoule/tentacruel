# pylint: disable=missing-docstring
from _asyncio import Future
from . service import _HeosService

# pylint: disable=too-many-public-methods
class _HeosPlayer(_HeosService):
    prefix = "player"

    def __init__(self, protocol, player_id=None):
        super().__init__(protocol)
        self.play_states = {"stop", "pause", "play"}
        self.mute_states = {"on", "off"}
        self.repeat_states = {"on_all", "on_one", "off"}
        self.shuffle_states = {"on", "off"}
        self._pid = player_id

    def pid(self):
        return self._pid

    async def get_players(self) -> Future:
        return await self._run(
            "get_players",
        )

    async def get_player_info(self) -> Future:

        return await self._run(
            "get_player_info",
            pid=self._pid
        )

    async def get_play_state(self) -> Future:
        return await self._run(
            "get_play_state",
            pid=self._pid
        )

    async def set_play_state(self, state="stop") -> Future:
        if state not in self.play_states:
            raise ValueError(f"Play state must be one of {self.play_states} instead of {state}")

        return await self._run(
            "set_play_state",
            pid=self._pid,
            state=state
        )

    async def get_now_playing_media(self) -> Future:
        return await self._run(
            "get_now_playing_media",
            pid=self._pid
        )

    async def get_volume(self) -> Future:
        return await self._run(
            "get_volume",
            pid=self._pid
        )

    async def set_volume(self, level=0) -> Future:
        return await self._run(
            "set_volume",
            pid=self._pid,
            level=level,
        )

    async def volume_up(self, step=5) -> Future:
        return await self._run(
            "volume_up",
            pid=self._pid,
            step=step
        )

    async def volume_down(self, step=5) -> Future:
        return await self._run(
            "volume_down",
            pid=self._pid,
            step=step
        )

    async def get_mute(self) -> Future:
        return await self._run(
            "get_mute",
            pid=self._pid
        )

    async def set_mute(self, state="on") -> Future:
        if state not in self.mute_states:
            raise ValueError(f"Mute state must be one of {self.mute_states} instead of {state}")

        return await self._run(
            "set_mute",
            pid=self._pid,
            state=state
        )

    async def toggle_mute(self) -> Future:
        return await self._run(
            "toggle_mute",
            pid=self._pid
        )

    async def get_play_mode(self) -> Future:
        return await self._run(
            "get_play_mode",
            pid=self._pid
        )

    async def set_play_mode(self, repeat="off", shuffle="off") -> Future:
        if repeat not in self.repeat_states:
            raise ValueError(
                f"Repeat state must be one of {self.repeat_states} instead of {repeat}"
            )

        if shuffle not in self.shuffle_states:
            raise ValueError(
                f"Shuffle state must be one of {self.shuffle_states} instead of {shuffle}"
            )

        return await self._run(
            "set_play_mode",
            pid=self._pid,
            repeat=repeat,
            shuffle=shuffle
        )

    async def get_queue(self, _range=None) -> Future:
        arguments = dict(pid=self._pid)
        if _range:
            arguments["range"] = _range

        return await self._run(
            "get_queue",
            **arguments
        )

    async def add_to_queue(self, sid=None, cid=None, mid=None, aid=None):
        if aid is None:
            aid = 4

        arguments = dict(
            pid=self._pid,
            aid=aid
        )
        if sid:
            arguments["sid"] = sid
        if cid:
            arguments["cid"] = cid
        if mid:
            arguments["mid"] = mid

        return await self._run(
            "add_to_queue",
            **arguments
        )

    async def play_queue(self, qid=1) -> Future:
        return await self._run(
            "play_queue",
            pid=self._pid,
            qid=qid
        )

    async def remove_from_queue(self, qid) -> Future:
        if not isinstance(qid, list):
            qid = [qid]

        return await self._run(
            "remove_from_queue",
            pid=self._pid,
            qid=",".join(map(str, qid))
        )

    #
    # this doesn't seem to be working at the moment!
    #

    async def save_queue(self, name: str) -> Future:
        if not name or len(name) > 128:
            raise ValueError("The playlist name must be less than 128 characters")

        return await self._run(
            "save_queue",
            pid=self._pid,
            name=name
        )

    async def clear_queue(self) -> Future:
        return await self._run(
            "clear_queue",
            pid=self._pid
        )

    async def play_next(self) -> Future:
        return await self._run(
            "play_next",
            pid=self._pid
        )

    async def play_previous(self) -> Future:
        return await self._run(
            "play_previous",
            pid=self._pid
        )

    async def play_stream(self, sid, cid, mid, name):
        return await self._run(
            "play_stream",
            id=sid,
            cid=cid,
            mid=mid,
            pid=self._pid,
            name=name
        )
