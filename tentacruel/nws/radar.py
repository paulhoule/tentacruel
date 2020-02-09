"""
Command line program to create movies for radar

"""
import argparse
from argparse import ArgumentParser
import datetime
import re

from asyncio import get_event_loop, current_task, sleep, wait
from logging import getLogger, StreamHandler
from os import environ
from sys import exc_info


from aiohttp import ClientConnectorError, ClientSession

from bus import bus_loop
from tentacruel.aio import handleClientConnectorError
from tentacruel.config import get_config, connect_to_adb
from tentacruel.nws import RadarFetch, register
from tentacruel.metar.log_wx import metar_cycle

LOG = getLogger(__name__)

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

def parse_arguments() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("-l","--loop",help="Continuously loop to periodically update radar and WX",action="store_true")
    return parser.parse_args()

async def amain() -> None:
    """
    Main method of radar fetcher program

    :return:
    """
    args = parse_arguments()
    if "LOGGING_LEVEL" in environ:
        getLogger(None).setLevel(environ["LOGGING_LEVEL"])
    getLogger(None).addHandler(StreamHandler())

    server_config = get_config("wx-paths.yaml")
    product_config = get_config("radar_config.yaml", package="tentacruel.nws")
    config = {**server_config, **product_config}
    adb = connect_to_adb(get_config())

    fetcher = RadarFetch(config, adb)
    if args.loop:
        await wait([
            video_loop(fetcher),
            metar_loop("KITH", adb.collection("metar")),
            bus_loop(adb.collection("bus"))
        ])
    else:
        await video_cycle(fetcher)

async def video_cycle(fetcher: RadarFetch):
    try:
        await fetcher.refresh()
    except ClientConnectorError as that:
        return handleClientConnectorError(that)

    fetcher.make_video()
    fetcher.make_forecast()
    return True

async def video_loop(fetcher:RadarFetch):
    while True:
        LOG.info("Fetching video")
        await video_cycle(fetcher)
        LOG.info("Complete video fetch")
        await sleep(300)

async def metar_loop(airport, collection):
    async with ClientSession() as session:
        while True:
            LOG.info("Fetching METAR")
            await metar_cycle(session, airport, collection)
            await sleep(30)

def main() -> None:
    """
    Main method of command line-program.  Creates event loop and then runs amain() in it

    :return: nothing
    """
    loop = get_event_loop()
    loop.run_until_complete(amain())

if __name__ == '__main__':
    main()
