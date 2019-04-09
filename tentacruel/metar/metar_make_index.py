"""
Command-line program to create index for metar table in adb

"""
from arango import ArangoClient
from tentacruel.config import get_config

def main() -> None:
    """
    main() method of command line program

    :return: None
    """
    config = get_config()

    adb_conf = config["arangodb"]["events"]
    client = ArangoClient(**adb_conf["client"])
    adb = client.db(**adb_conf["database"])
    collection = adb.collection("metar")
    collection.add_skiplist_index(["station", "time"])

if __name__ == '__main__':
    main()
