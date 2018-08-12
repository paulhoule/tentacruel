from asyncio import Future

from . service import _HeosService


class _HeosBrowse(_HeosService):
    prefix = "browse"

    async def get_music_sources(self) -> Future:
        return await self._run("get_music_sources")

    async def get_source_info(self,sid: int) -> Future:
        return await self._run("get_source_info",
            dict(sid=sid)
        )

    async def browse(self, sid:int, cid:str = None) -> Future:
        args = {"sid":sid}
        if cid:
            args["cid"] = cid

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
