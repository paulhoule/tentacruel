"""
Configuration-related functions.

Read YAML configuration,  connect to databases,  etc.
"""

from pathlib import Path
import yaml

def connect_to_adb(config):
    """
    Connect to arango database (duplicated all over I know)

    :param config:
    :return: connection to database
    """
    from arango import ArangoClient
    client = ArangoClient(**config["arangodb"]["events"]["client"])
    return client.db(**config["arangodb"]["events"]["database"])


def get_config():
    """
    Read tentacruel configuration file

    :return:
    """
    with open(Path.home() / ".tentacruel" / "config.yaml") as config:
        return yaml.load(config)
