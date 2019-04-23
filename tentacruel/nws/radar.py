"""
Command line program to create movies for radar

"""
import datetime
import re

from asyncio import get_event_loop
from logging import getLogger, StreamHandler
from os import environ
from sys import exc_info


from aiohttp import ClientConnectorError
from tentacruel.config import get_config
from tentacruel.nws import RadarFetch, register

from _socket import gaierror


@register
def radar_file_date(name: str) -> datetime.datetime:
    """
    Compute date based on pattern on name of radar file

    :param name:
    :return:
    """
    file_pattern = re.compile(r"_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(?:_N0R|_N1P)?.gif$")
    match = file_pattern.search(name)
    if not match:
        return None

    (year, month, day, hour, minute) = map(int, match.groups())
    return datetime.datetime(year, month, day, hour, minute, tzinfo=datetime.timezone.utc)

async def amain() -> None:
    """
    Main method of radar fetcher program

    :return:
    """
    if "LOGGING_LEVEL" in environ:
        getLogger(None).setLevel(environ["LOGGING_LEVEL"])

    getLogger(None).addHandler(StreamHandler())

    server_config = get_config("wx-paths.yaml")
    product_config = get_config("radar_config.yaml", package="tentacruel.nws")
    config = {**server_config, **product_config}

    fetcher = RadarFetch(config)
    try:
        await fetcher.refresh()
    except ClientConnectorError:
        (_, exception, _) = exc_info()
        inner_exception = exception.os_error
        if isinstance(inner_exception, gaierror) and "Temporary" in str(inner_exception):
            return
        if isinstance(inner_exception, OSError):
            if "Network is unreachable" in str(inner_exception):
                return
            if "Connect call failed" in str(inner_exception):
                return
        raise
    fetcher.make_video()

def main() -> None:
    """
    Main method of command line-program.  Creates event loop and then runs amain() in it

    :return: nothing
    """
    loop = get_event_loop()
    loop.run_until_complete(amain())

if __name__ == '__main__':
    main()
