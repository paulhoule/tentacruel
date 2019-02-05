from _asyncio import Future
from typing import List

from . service import _HeosService

class _HeosGroup(_HeosService):
    prefix = "group"

    def __init__(self,protocol):
        super().__init__(protocol)

    async def get_groups(self) -> Future:
        return await self._run(
            "get_groups",
        )

    async def set_group(self,pid:List[int]) -> Future:
        return await self._run(
            "set_group",
            arguments=dict(pid=",".join(map(str,pid)))
        )


