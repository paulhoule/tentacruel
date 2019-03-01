# pylint: disable=missing-docstring
from _asyncio import Future
from . service import _HeosService

# pylint: disable=too-few-public-methods
class _HeosSystem(_HeosService):
    prefix = "system"

    async def register_for_change_events(self, enable=True) -> Future:
        future = self._run(
            "register_for_change_events",
            enable="on" if enable else "off"
        )

        await future
