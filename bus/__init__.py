"""
Fetch TCAT bus information

"""
import json
import time
from asyncio import sleep
from logging import getLogger
from typing import Dict, Any

from aiohttp import ClientSession
from arango.collection import Collection

from tentacruel.aio import afetch
from tentacruel.time import utcnow, to_zulu_string

LOG = getLogger(__name__)
async def get_bus(session: ClientSession, route: str) -> Dict[str, Any]:
    url = f"https://realtimetcatbus.availtec.com/InfoPoint/rest/Vehicles/GetAllVehiclesForRoutes?routeIDs={route}"
    text = await afetch(session, url)
    return {"buses": json.loads(text)}

async def bus_cycle(session: ClientSession, collection: Collection):
    bus_data = await get_bus(session,"52,53")
    timestamp_id = "{:016d}".format(int(round(time.time()-1576684879,2)*100))
    bus_data["_key"] = timestamp_id
    bus_data["observed"] = to_zulu_string(utcnow())
    print("[About to fetch]")
    result = collection.insert(bus_data)
    print("[My result]")

async def bus_loop(collection: Collection):
    try:
        async with ClientSession() as session:
            while True:
                LOG.info("Fetching Bus Location")
                await bus_cycle(session, collection)
                await sleep(30)
    except Exception as ex:
        LOG.critical("bus_loop failed with Exception:", ex)
