"""
Command line program to harvest METAR information for KITH airport

"""

from asyncio import get_event_loop
from logging import getLogger
from sys import exc_info, argv

from aiohttp import ClientSession, ClientConnectorError
from _socket import gaierror

LOGGER = getLogger(__name__)

async def amain() -> None:
    """
    Aynchronous main method of command-line program.  Async so it can call async
    methods without messing around with event loops.

    :return: nothing
    """

    async with ClientSession() as session:
        reply = await session.get(argv[1])
        raw = await reply.read()
        print(raw.decode())

    LOGGER.debug("End of amain() method")

def main() -> None:
    """
    Main method of command line-program.  Creates event loop and then runs amain() in it

    :return: nothing
    """
    loop = get_event_loop()
    loop.run_until_complete(amain())

if __name__ == '__main__':
    main()
