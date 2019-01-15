import asyncio

class _HeosService():
    def __init__(self,protocol):
        self.protocol=protocol

    def _run(self,command,arguments={}) -> asyncio.futures.Future:
        prefix = self.__class__.prefix
        return self.protocol._run_command(prefix + "/" + command, arguments)