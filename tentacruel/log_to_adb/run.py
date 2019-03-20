"""
Log smartthings-style events from the message queue to arangodb
"""
from asyncio import run

from tentacruel.log_to_adb import LogToADB

if __name__ == "__main__":
    # pylint: disable=invalid-name
    adb_logger = LogToADB()
    run(adb_logger.log_events())
