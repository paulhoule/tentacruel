"""

GUI application to watch system status.

"""

from asyncio import run, get_event_loop, create_task
from logging import getLogger, StreamHandler, DEBUG
from os import environ
from tkinter import Label
from tkinter.font import Font
from typing import Any, Dict, List
import json
from uuid import uuid4

from aio_pika import connect_robust, Connection, ExchangeType
from arango.database import Database
from tentacruel.config import get_config, connect_to_adb
from tentacruel.gui import ManagedGridFrame, run_tk
from tentacruel.watch_gui import local_from_iso_zulu, extract_sensor_list

LOGGER = getLogger(__name__)

# pylint: disable=too-many-ancestors
# pylint: disable=too-many-instance-attributes
class Application(ManagedGridFrame):
    """
    This application shows a visual display of the system state,  for instance,
    the state of the motion detectors,  and updates the image as messages
    come in on the queue.

    """

    def __init__(self,
                 config: Dict[str, Any],
                 attributes: List[str],
                 **kwargs):
        """

        :param config: tentacruel configuration dictionary;  this is not saved
        in the constructor.  But the constructor may validate it and set other
        variables in response to the configuration
        """
        if len(attributes) == 1:
            kwargs["columns"] = 3
            self.has_since = True
        else:
            kwargs["columns"] = 1 + len(attributes)
            self.has_since = False

        super().__init__(**kwargs)

        self.alive = True
        self._pika_config = config["pika"]
        self.pika: Connection = None
        self.adb: Database = connect_to_adb(config)
        self.attributes = attributes

        BOLD = Font(weight="bold") # pylint: disable=invalid-name
        self._add("header-label", Label, text="label", font=BOLD)
        for attribute in attributes:
            self._add("header-a-" + attribute, Label, text=attribute, font=BOLD)
        if len(attributes) == 1:
            self._add("header-since", Label, text="since", font=BOLD)

        sensors = extract_sensor_list(self.adb)
        self.sensor_by_key = {}
        for sensor in sensors:
            self.sensor_by_key[sensor["sensor_id"]] = sensor
            self._add(sensor["sensor_id"] + "-label", Label, text=sensor["name"])
            for attribute in attributes:
                self._add(sensor["sensor_id"] + "-a-" + attribute, Label, text="Unknown")
            if len(attributes) == 1:
                self._add(sensor["sensor_id"] + "-since", Label, text=" "*8)

        self.label_states = {
            "active": {
                "text": "active",
                "background": "green",
                "foreground": "black"
            },
            "inactive":{
                "text" : "inactive",
                "background": "red",
                "foreground": "white"
            }
        }

    async def setup(self) -> None:
        """
        Setup stage completed asynchronously so we can use asynchronous
        facilities to do the setup

        Note we do not await here,  but use create_task() to schedule the
        app to run later so the caller can launch additional tasks.

        :return:
        """

        create_task(self.fetch_and_listen())

    async def fetch_and_listen(self) -> None:
        """
        "Main loop" of program:  fetch pseudo-events from arangodb to get current
        attribute values.  Then fetch real events to keep attributes up to date

        :return:
        """
        await self.fetch_events()
        await self.listen_on_queue()

    async def fetch_events(self) -> None:
        """
        Fetch psuedo-events from the 'attributes' table.  These are the attribute values of the last
        events that happened to the system,  that,  we catch up with the existing state by replaying
        these events and henceforth update the user interface accordingly.

        :return:
        """
        aql_query = """
            for row in attributes
                filter row._key IN @devices
                for attribute in attributes(row)
                   filter left(attribute,1) != "_"
                   return merge(row[attribute],{"attribute": attribute,"deviceId": row._key})
        """
        bind_vars = {
            "devices": list(self.sensor_by_key.keys())
        }
        current_status = list(self.adb.aql.execute(aql_query, bind_vars=bind_vars))
        for event in current_status:
            event = await self.enrich_event(event)
            await self.handle_event(event)

    async def listen_on_queue(self) -> None:
        """
        Loop on message queue to get motion events and pass to GUI.

        Does not return.

        :return:
        """
        connection: Connection = await connect_robust(
            loop=get_event_loop(),
            **self._pika_config
        )

        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                'smartthings',
                ExchangeType.FANOUT
            )

            queue = await channel.declare_queue(exclusive=True)
            await queue.bind(exchange, routing_key="motion")

            async with queue.iterator() as messages:
                async for message in messages:
                    with message.process():
                        event = json.loads(message.body)
                        await self.handle_event(event)

    async def enrich_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich event record with information from database

        :param event: dictionary with event data,  left unchanged by this function
        :return: dictionary enriched with additional fields based on device metadata
        """
        result = event.copy()

        # if an event doesn't have an event id,  give it one because consumers
        # will assume it has one (e.g. event is pseudo event with current state
        # information)

        if "_key" not in result:
            result["_key"] = uuid4()
        device_id = event["deviceId"]
        if device_id in self.sensor_by_key:
            result["deviceName"] = self.sensor_by_key[device_id]["name"]

        return result

    async def handle_event(self, event: Dict[str, Any]) -> None:
        """

        :param event: Dictionary of key/value pairs identified by the key "_key"
        :return: Nothing
        """
        event = await self.enrich_event(event)
        if LOGGER.isEnabledFor(DEBUG):
            await self.log_event(event)
        await self.update_ui(event)

    async def log_event(self, event: Dict[str, Any]) -> None:
        """
        Write event to log.

        :param event: Dictionary of key/value pairs identified by the key "_key"
        :return: nothing
        """
        event_id = event["_key"]
        LOGGER.debug("==== Event Recieved ============================")
        for (key, value) in event.items():
            if key != "_key":
                LOGGER.debug("Event id (%s):  %s = %s", event_id, key, value)

    async def update_ui(self, event) -> None:
        """
        Update user interface from event
        :param event:
        :return:
        """
        device_id = event["deviceId"]
        if event["attribute"] in self.attributes:
            if device_id in self.sensor_by_key:
                label = self[device_id + "-a-" + event["attribute"]]
                if event["attribute"] == "motion":
                    options = self.label_states[event["value"]]
                    for (option_name, option_value) in options.items():
                        label[option_name] = option_value
                else:
                    label["text"] = event["value"]

                if self.has_since:
                    since = self[device_id + "-since"]
                    if "eventTime" in event:
                        when = local_from_iso_zulu(event["eventTime"])
                        since["text"] = when.time().isoformat()


async def amain() -> None:
    """
    amain is a main method,  but it is asynchronous,  main() jumps into here
    right away where we initialize the application and then start polling
    the tk event loop to handle gui events together with asyncio

    :return:
    """
    config = get_config()
    attributes = [
        "temperature",
        "humidity",
        "illuminance",
        "motion",
        "battery"
    ]
    app = Application(config, attributes)
    await app.setup()
    await run_tk(app)

def main() -> None:
    """
    main method of application,  expressed as a function so pylint won't
    complain about how I use the main namespace.  Boots asynchronous main
    method inside default event loop.

    :return:
    """
    if "LOGGING_LEVEL" in environ:
        getLogger(None).setLevel(environ["LOGGING_LEVEL"])
    getLogger(None).addHandler(StreamHandler())

    run(amain())

if __name__ == "__main__":
    main()
