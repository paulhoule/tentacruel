from sys import exc_info
from _socket import gaierror

from aiohttp import ClientConnectorError, ClientSession


def handleClientConnectorError(that: ClientConnectorError):
    """
    Error handling routine to be run in an ``except catchClientConnectorError:``` clause.

    Catches transient errors caused by interruptions in internet service:  if the program
    waits a while,  the service will probably come back

        :param: that a ClientConnectorError
        :returns: False if it returns,  indicating that the operation failed in a possibly
                  transient way.
        :raises ClientConnectorError: if the error is likely to be permanent
    """
    (_, exception, _) = exc_info()
    inner_exception = exception.os_error
    if isinstance(inner_exception, gaierror) and "Temporary" in str(inner_exception):
        return False
    if isinstance(inner_exception, OSError):
        if "Network is unreachable" in str(inner_exception):
            return False
        if "Connect call failed" in str(inner_exception):
            return False
    raise


async def afetch(session: ClientSession, url: str):
    """
    Asynchronous fetch.  Do a GET request,  return text,  properly  shutdown

    :param session: ClientSession object for aiohttp connection
    :param url: The URL we want
    :return:
    """
    async with session.get(url) as response:
        return await response.text()