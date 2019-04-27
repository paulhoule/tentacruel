"""
Functions associated with the GUI program for viewing the system state in real time

"""

import datetime

import pytz
from arango.database import Database


EST = pytz.timezone("US/Eastern")
def local_from_iso_zulu(that: str) -> datetime.datetime:
    """
    Convert an ISO formatted datetime in string form to a
    datetime.datetime object zoned to the local timezone

    :param that: e.g. ''"2019-04-15T17:45:16"''
    :return: e.g::
       datetime.datetime(2019, 4, 15, 14, 24, 49,
          tzinfo=<DstTzInfo 'US/Eastern' EDT-1 day, 20:00:00 DST>)

    from above input in US/Eastern.
    """

    raw_time = datetime.datetime.fromisoformat(that.replace("Z", ""))
    utc_time = raw_time.replace(tzinfo=datetime.timezone.utc)
    return utc_time.astimezone(EST)


def extract_sensor_list(adb: Database):
    """
    Find sensors in configuration file and return them as a list

    :param config: arangodb database
    :return: a list of dicts that look like::

        {
            "sensor_id": "a20bab2e-a7d0-4c93-8723-27a7bf3299b6",
            "name": "inner-doghouse"
        }

        defining what sensors to show in GUI.
    """
    aql_query = """
    for row in names
        return {"name": row._key ,"sensor_id": row.deviceId}
    """

    sensors = list(adb.aql.execute(aql_query))
    return sensors
