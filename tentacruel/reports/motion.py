# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from pathlib import Path
from collections import Counter

import pytz
import yaml
from tentacruel.time import from_zulu_string

with open(Path.home() / ".tentacruel" / "config.yaml") as a_stream:
    config = yaml.load(a_stream)


def connect_to_adb():
    from arango import ArangoClient
    client = ArangoClient(**config["arangodb"]["events"]["client"])
    return client.db(**config["arangodb"]["events"]["database"])

db = connect_to_adb()
cursor = db.aql.execute("""
    for event in sqs_events
       FILTER event.attribute == 'motion'
       FILTER event.eventTime > '2019-03-03T03:00:00'
       FILTER event.eventTime < '2019-03-03T13:00:00'
       SORT event.eventTime
       return keep(event,"eventTime","deviceId","value")
""")

def map_it(that):
    result = {}
    result["deviceId"] = that["deviceId"]
    result["value"] = that["value"]
    event_zulu = from_zulu_string(result["eventTime"])
    EST = pytz.timezone("US/Eastern")
    result["eventTime"] = event_zulu.astimezone(EST)

    return result

items = [map_it(x) for x in cursor]
active_times = [x["eventTime"].hour for x in items if x['value'] == 'active']

c = Counter()
for x in active_times:
    c[x] += 1

hr = [22, 23] + list(range(8))
for idx in hr:
    cnt = c.get(idx, 0)
    print(f"{idx}: {cnt}")
