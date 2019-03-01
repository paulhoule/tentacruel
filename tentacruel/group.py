# pylint: disable=missing-docstring
from typing import List
from _asyncio import Future
from . service import _HeosService

class _HeosGroup(_HeosService):
    prefix = "group"

    async def get_groups(self) -> Future:
        return await self._run("get_groups",)

    async def set_group(self, pid: List[int]) -> Future:
        return await self._run(
            "set_group",
            pid=",".join(map(str, pid))
        )
