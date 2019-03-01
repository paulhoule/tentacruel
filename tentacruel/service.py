# pylint: disable=missing-docstring
import asyncio

# pylint: disable=too-few-public-methods
class _HeosService():
    def __init__(self, protocol):
        self.protocol = protocol

    def _run(self, command, **arguments) -> asyncio.futures.Future:
        # pylint: disable=no-member
        prefix = self.__class__.prefix
        # pylint: disable=protected-access
        return self.protocol._run_command(prefix + "/" + command, **arguments)
