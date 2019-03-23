"""
Collected report generators for common tasks.

What these have in common is that they don't depend on pandas or similar libraries
but they do return results as a dict-of-list as opposed to list-of-dicts which is
how they are stored in pandas.

"""
import datetime
from uuid import UUID

from arango.database import StandardDatabase

def parse_iso8601_zulu(then):
    """
    :param then: a string date in the format '2019-03-20T20:40:48Z' which has to
           be a GMT date ending in Z
    :return: converted datetime
    """
    if then[-1] != "Z":
        raise ValueError(f"Date {then} does not end in Z like a GMT date should")

    return datetime.datetime.fromisoformat(then[:-1])

class ReportGenerator:
    # pylint: disable=too-few-public-methods
    """
    Class to hang report generators on

    """
    def __init__(self, adb: StandardDatabase):
        self.adb = adb

    def timeseries(self, device_id: UUID, attribute: str, value_type=float):
        """
        Time Series Report.  Returns values ordered by event time

        :param device_id: UUID of device
        :param attribute: desired attribute
        :param value_type: type of value.  defaults to float.  Really we use this
                           as a function to do the type conversion
        :return: a dictionary with two keys ``eventTime`` and ``value``) the first
                 is a parsed ISO date and ``value`` is of type ``value_type``
        """
        cursor = self.adb.aql.execute("""
            for event in sqs_events
                filter event.deviceId == @device_id
                filter event.attribute == @attribute
                sort event.eventTime
                return keep(event,"eventTime","value")
        """, bind_vars={
            "device_id": str(device_id),
            "attribute": attribute
            })

        event_time = []
        value = []
        for row in cursor:
            event_time.append(parse_iso8601_zulu(row["eventTime"]))
            value.append(value_type(row["value"]))
        return {
            "eventTime": event_time,
            "value": value
        }
