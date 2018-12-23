from asyncio import Future

from . service import _HeosService


class _HeosBrowse(_HeosService):
    prefix = "browse"

    def _get_player_id(self):
        return self.protocol._player_id

    async def get_music_sources(self) -> Future:
        return await self._run("get_music_sources")

    async def get_source_info(self,sid: int) -> Future:
        return await self._run("get_source_info",
            dict(sid=sid)
        )

    async def browse(self, sid:int, cid:str = None, range = None) -> Future:
        args = {"sid":sid}
        if cid:
            args["cid"] = cid

        if range:
            args["range"] = range

        return await self._run("browse",
            args
        )

    #
    # not in HEOS api but it makes coding against the HEOS API much easier
    #

    async def browse_for_name(self,name,sid,*args,**kwargs):
        if isinstance(name,list):
            for subname in name:
                result = await self.browse_for_name(subname,sid,*args,**kwargs)
                args = [result["cid"]]
            return result

        else:
            result = await self.browse(sid,*args,**kwargs)
            payload = result["payload"]
            for media in payload:
                if media["name"] == name:
                    return media

            raise KeyError("Could not find object with name "+media)

    async def get_search_criteria(self, sid:int) -> Future:
        return await self._run("get_search_criteria",{"sid":sid})

    #
    # I am currently getting "System error" when I test this.  I notice that
    # I can't find a search function in the Android app.
    #

    async def search(self, sid:int, search: str,scid: int):
        return await self._run("search",{
            "sid": sid,
            "search": search,
            "scid": scid
        })

    async def play_stream(self, sid:int, cid:int, mid:int, name: str, pid:int = None):
        if pid==None:
            pid=self._get_player_id()
        return await self._run("play_stream",{
            "pid": pid,
            "sid": sid,
            "mid": mid,
            "cid": cid,
            "name": name
        })