from pathlib import Path

import yaml
from pkg_resources import resource_string

with open(Path.home() / ".tentacruel" / "config.yaml") as a_stream:
    config = yaml.load(a_stream)

def connect_to_adb():
    from arango import ArangoClient
    client = ArangoClient(**config["arangodb"]["events"]["client"])
    return client.db(**config["arangodb"]["events"]["database"])

db = connect_to_adb()

query = resource_string("tentacruel.aql", "event-delays.aql").decode()

cols = ['when', 'attribute', 'value', 'lambdaDelay', 'enqueuedDelay', 'receiveDelay', 'drainDelay', 'logDelay']
cursor = list(db.aql.execute(query,bind_vars = {"attributes": ["switch"]}))

lens = [len(col) for col in cols]
for row in cursor:
    for idx, key in enumerate(cols):
        lens[idx] = max(lens[idx], len(str(row[key])))

print(" ".join(format(c,str(l)) for (c,l) in zip(cols,lens)))
print(" ".join('='*l for l in lens))

for row in cursor:
    cells = []
    for key, length in zip(cols, lens):
        value = row[key]
        if value is None:
            value="-"
        cell = format(value,f"{length}")
        cells.append(cell)
    print(" ".join(cells))

