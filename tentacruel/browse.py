# pylint: disable=missing-docstring
from asyncio import Future

from . service import _HeosService


class _HeosBrowse(_HeosService):
    prefix = "browse"

    async def get_music_sources(self) -> Future:
        return await self._run("get_music_sources")

    async def get_source_info(self, sid: int) -> Future:
        return await self._run("get_source_info", sid=sid)

    async def browse(
            self,
            sid: int,
            cid: str = None,
            _range=None
    ) -> Future:
        args = {"sid":sid}
        if cid:
            args["cid"] = cid

        if _range:
            args["range"] = _range

        return await self._run("browse", **args)

    #
    # not in HEOS api but it makes coding against the HEOS API much easier
    #

    async def browse_for_name(self, name, sid, *args, **kwargs):
        if isinstance(name, list):
            for subname in name:
                result = await self.browse_for_name(subname, sid, *args, **kwargs)
                args = [result["cid"]]
            return result

        result = await self.browse(sid, *args, **kwargs)
        payload = result["payload"]
        for media in payload:
            if media["name"] == name:
                return media

        raise KeyError("Could not find object with name "+name)

    async def get_search_criteria(self, sid: int) -> Future:
        return await self._run("get_search_criteria", sid=sid)

    #
    # I am currently getting "System error" when I test this.  I notice that
    # I can't find a search function in the Android app.
    #

    async def search(self, sid: int, search: str, scid: int):
        return await self._run(
            "search",
            sid=sid,
            search=search,
            scid=scid
        )

    async def add_to_queue(self, pid, sid=None, cid=None, mid=None, aid=None):
        if aid is None:
            aid = self.REPLACE_AND_PLAY

        arguments = dict(
            pid=pid,
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