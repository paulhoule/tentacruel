"""
Command line program to harvest METAR information for KITH airport

"""

from asyncio import get_event_loop
from logging import getLogger
from sys import exc_info

from aiohttp import ClientSession, ClientConnectorError
from arango import ArangoClient, DocumentInsertError
from tentacruel.config import get_config, configure_logging
from tentacruel.metar import get_metar

from _socket import gaierror

LOGGER = getLogger(__name__)

async def amain() -> None:
    """
    Aynchronous main method of command-line program.  Async so it can call async
    methods without messing around with event loops.

    :return: nothing
    """
    config = get_config()
    configure_logging()

    adb_conf = config["arangodb"]["events"]
    client = ArangoClient(**adb_conf["client"])
    adb = client.db(**adb_conf["database"])
    collection = adb.collection("metar")

    airport = "KITH"
    async with ClientSession() as session:
        try:
            metar = await get_metar(session, airport)
        except ClientConnectorError:
            (_, exception, _) = exc_info()
            inner_exception = exception.os_error
            if isinstance(inner_exception, gaierror) and "Temporary" in str(inner_exception):
                return
            raise
        try:
            LOGGER.debug(metar)
            collection.insert(metar, silent=True)
        except DocumentInsertError:
            pass
        LOGGER.debug("About to shut down http client session")
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
