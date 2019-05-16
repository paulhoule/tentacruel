"""
Configuration-related functions.

Read YAML configuration,  connect to databases,  etc.
"""
from logging import getLogger, StreamHandler
from os import environ
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

def connect_to_sqs(config):
    """
    Given configuration dictionary,  return a boto3 connection for SQS

    :param config: application config dictionary
    :return: SQS connection object from boto3
    """
    from boto3 import client
    return client(
        "sqs",
        aws_access_key_id=config["aws"]["aws_access_key_id"],
        aws_secret_access_key=config["aws"]["aws_secret_access_key"],
        region_name=config["aws"]["region_name"]
    )

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

def configure_logging() -> None:
    """
    Configure logging. Call once in the "main()" method of an application so
    that we can switch debug logging on when necessary

    :return: Nothing,  only has side effects
    """
    if "LOGGING_LEVEL" in environ:
        getLogger(None).setLevel(environ["LOGGING_LEVEL"])

    getLogger(None).addHandler(StreamHandler())
