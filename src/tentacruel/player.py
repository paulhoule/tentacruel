from _asyncio import Future

from . service import _HeosService

class _HeosPlayer(_HeosService):
    prefix = "player"

    def __init__(self,protocol):
        self.play_states = {"stop", "pause", "play"}
        self.mute_states = {"on", "off"}
        self.repeat_states = {"on_all","on_one","off"}
        self.shuffle_states = {"on", "off"}
        self.protocol=protocol

    def _get_player_id(self):
        return self.protocol._player_id

    async def get_players(self) -> Future:
        return await self._run(
            "get_players",
        )

    async def get_player_info(self,pid = None) -> Future:
        if pid==None:
            pid=self._get_player_id()

        return await self._run(
            "get_player_info",
            arguments = dict(pid = pid)
        )

    async def get_play_state(self,pid = None) -> Future:
        if pid==None:
            pid=self._get_player_id()

        return await self._run(
            "get_play_state",
            arguments = dict(pid = pid)
        )

    async def set_play_state(self,state = "stop",pid = None,) -> Future:
        if state not in self.play_states:
            raise ValueError(f"Play state must be one of {self.play_states}3 instead of {state}")

        if pid==None:
            pid=self._get_player_id()

        return await self._run(
            "set_play_state",
            arguments = dict(pid = pid,state=state)
        )

    async def get_now_playing_media(self,pid = None) -> Future:
        if pid==None:
            pid=self._get_player_id()

        return await self._run(
            "get_now_playing_media",
            arguments = dict(pid = pid)
        )

    async def get_volume(self,pid = None) -> Future:
        if pid==None:
            pid=self._get_player_id()

        return await self._run(
            "get_volume",
            arguments = dict(pid = pid)
        )

    async def set_volume(self,level = 0,pid = None) -> Future:
        if pid==None:
            pid=self._get_player_id()

        return await self._run(
            "set_volume",
            arguments = dict(pid = pid,level = level)
        )

    async def volume_up(self,pid = None,step = 5) -> Future:
        if pid==None:
            pid=self._get_player_id()

        return await self._run(
            "volume_up",
            arguments = dict(pid = pid,step = step)
        )

    async def volume_down(self,pid = None,step = 5) -> Future:
        if pid==None:
            pid=self._get_player_id()

        return await self._run(
            "volume_down",
            arguments= dict(pid = pid,step = step)
        )

    async def get_mute(self,pid = None) -> Future:
        if pid==None:
            pid=self._get_player_id()

        return await self._run(
            "get_mute",
            arguments= dict(pid = pid)
        )

    async def set_mute(self,pid = None,state = "on") -> Future:
        if state not in self.mute_states:
            raise ValueError(f"Mute state must be one of {self.mute_states} instead of {state}")

        if pid==None:
            pid=self._get_player_id()

        return await self._run(
            "set_mute",
            arguments= dict(pid = pid,state=state)
        )

    async def toggle_mute(self,pid = None) -> Future:
        if pid==None:
            pid=self._get_player_id()

        return await self._run(
            "toggle_mute",
            arguments= dict(pid = pid)
        )

    async def get_play_mode(self,pid = None) -> Future:
        if pid==None:
            pid=self._get_player_id()

        return await self._run(
            "get_play_mode",
            arguments= dict(pid = pid)
        )

    async def set_play_mode(self,repeat="off",shuffle="off",pid = None) -> Future:
        if pid==None:
            pid=self._get_player_id()

        if repeat not in self.repeat_states:
            raise ValueError(f"Repeat state must be one of {self.repeat_states} instead of {repeat}")

        if shuffle not in self.shuffle_states:
            raise ValueError(f"Shuffle state must be one of {self.shuffle_states} instead of {shuffle}")

        return await self._run(
            "set_play_mode",
            arguments= dict(pid = pid, repeat=repeat, shuffle=shuffle)
        )

    async def get_queue(self,range=None,pid = None) -> Future:
        if pid==None:
            pid=self._get_player_id()

        arguments = dict(pid = pid)
        if range:
            arguments["range"] = range

        return await self._run(
            "get_queue",
            arguments= arguments
        )

    async def play_queue(self,qid=1,pid = None) -> Future:
        if pid==None:
            pid=self._get_player_id()

        return await self._run(
            "play_queue",
            arguments= dict(pid=pid,qid=qid)
        )

    async def remove_from_queue(self,qid=[],pid=None) -> Future:
        if pid==None:
            pid=self._get_player_id()

        if not isinstance(qid,list):
            qid=list(qid)

        return await self._run(
            "remove_from_queue",
            arguments= dict(pid=pid,qid=",".join(map(str,qid)))
        )

