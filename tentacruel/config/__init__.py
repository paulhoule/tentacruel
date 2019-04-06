"""
Configuration-related functions.

Read YAML configuration,  connect to databases,  etc.
"""

from pathlib import Path
import yaml
from pkg_resources import resource_stream


def connect_to_adb(config):
    """
    Connect to arango database (duplicated all over I know)

    :param config:
    :return: connection to database
    """
    from arango import ArangoClient
    client = ArangoClient(**config["arangodb"]["events"]["client"])
    return client.db(**config["arangodb"]["events"]["database"])


def get_config(config_file="config.yaml", package=None):
    """
    Read tentacruel configuration file

    :return:
    """
    if package:
        with resource_stream(package, config_file) as config:
            return yaml.load(config)

    with open(Path.home() / ".tentacruel" / config_file) as config:
        return yaml.load(config)
