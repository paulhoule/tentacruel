from asyncio import Future


class _HeosService():
    def __init__(self,protocol):
        self.protocol=protocol

    def _run(self,command,arguments={}) -> Future:
        prefix = self.__class__.prefix
        return self.protocol._run_command(prefix + "/" + command, arguments)