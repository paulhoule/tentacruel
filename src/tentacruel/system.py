from _asyncio import Future

from . service import _HeosService

class _HeosSystem(_HeosService):
    prefix = "system"

    def __init__(self,protocol):
        self.protocol=protocol

    async def register_for_change_events(self,enable=True) -> Future:
        future = self._run(
            "register_for_change_events",
            dict(enable = "on" if enable else "off")
        )

        await future
