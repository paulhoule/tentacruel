"""
Fetch METAR data from National Weather Service

"""

import math
from typing import Dict, Any

from metar.Metar import Metar
from aiohttp import ClientSession

async def afetch(session: ClientSession, url: str):
    """
    Asynchronous fetch.  Do a GET request,  return text,  properly  shutdown

    :param session: ClientSession object for aiohttp connection
    :param url: The URL we want
    :return:
    """
    async with session.get(url) as response:
        return await response.text()

async def get_metar(session: ClientSession, airport: str) -> Dict[str, Any]:
    """
    Fetch METAR from specified airport and return transformed form.

    :param session: ClientSession object for aiohttp connection
    :param airport: 4-letter ICAO airport code (e.g. KITH)
    :return: Dictionary with parsed METAR results
    """
    stations = f"http://tgftp.nws.noaa.gov/data/observations/metar/stations/"
    url = f"{stations}/{airport}.TXT"
    text = await afetch(session, url)
    parts = text.split('\n')
    metar = internal_metar(parts[1])
    assign_key(metar)
    return metar

def rel_humidity(temp: float, dewpt: float) -> float:
    """
    Compute relative humidity from temperature and dew point

    :param temp: temperature in degrees F
    :param dewpt: dewpoint in degrees F
    :return: relative humidity as a percentage
    """
    return 100.0 * (math.exp((17.625 * dewpt) / (243.04 + dewpt)) /
                    math.exp((17.625 * temp) / (243.04 + temp)))

def internal_metar(metar_text: str) -> Dict[str, Any]:
    """
    Convert the output of the Metar parser into a dictionary which could be
    queried in a document database

    :param metar_text: metar string
    :return: a Dict with decoded METAR information
    """
    document = {}
    wxd = Metar(metar_text)
    document["station"] = wxd.station_id

    if wxd.type:
        document["type"] = wxd.type

    if wxd.time:
        document["time"] = wxd.time.isoformat()+'Z'

    if wxd.temp:
        document["temp"] = wxd.temp.value(units="F")

    if wxd.dewpt:
        document["dewpt"] = wxd.dewpt.value(units="F")

    if "temp" in document and "dewpt" in document:
        document["humidity"] = rel_humidity(document["temp"], document["dewpt"])

    if wxd.wind_speed:
        document["wind_speed"] = wxd.wind_speed.value(units="mph")

    if wxd.wind_dir:
        document["wind_dir"] = wxd.wind_dir.value()

    if wxd.vis:
        document["visibility"] = wxd.vis.value(units="sm")

    if wxd.press:
        document["pressure"] = wxd.press.value(units="mb")

    if wxd.sky:
        document["sky"] = wxd.sky_conditions()

    if wxd.press_sea_level:
        document["pressure"] = wxd.press_sea_level.value("mb")

    document["code"] = wxd.code

    return document

def assign_key(metar_data: Dict[str, Any]) -> None:
    """
    Append the ``_key`` field that arangodb insists on

    :param metar_data: a Dict containing metar data
    :return: nothing
    """
    parts = metar_data["code"].split(" ")
    metar_data["_key"] = metar_data["station"] + '-' + '201811' + '-' + parts[1]
