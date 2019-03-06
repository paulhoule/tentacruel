# pylint: disable=missing-docstring
# pylint: disable=invalid-name

"""
A thin layer around pika to simplify idiomatic asyncio programming.
with pika

"""

from asyncio import Future, Queue
from pathlib import Path

import yaml
from pika.channel import Channel
from pika.credentials import PlainCredentials
from pika.connection import Parameters, Connection
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.frame import Method

with open(Path.home() / ".tentacruel" / "config.yaml") as a_stream:
    config = yaml.load(a_stream)

async def asyncio_connection(pika_parameters: Parameters):
    wait_for = Future()
    AsyncioConnection(
        pika_parameters,
        on_open_callback=wait_for.set_result,
        on_open_error_callback=lambda item, message: wait_for.set_exception(IOError(message))
    )
    return await wait_for

async def open_channel(connection: Connection) -> Channel:
    wait_for = Future()
    connection.channel(wait_for.set_result)
    return await wait_for

async def queue_declare(channel: Channel, **args) -> Method:
    wait_for = Future()
    channel.queue_declare(wait_for.set_result, **args)
    return await wait_for

async def basic_consume(channel: Channel, **kwargs):
    inner_queue = Queue()

    def got_message(*args):
        inner_queue.put_nowait(("message", args))

    def channel_closed(*args):
        inner_queue.put_nowait(("closed", args))

    channel.add_on_close_callback(channel_closed)
    channel.basic_consume(
        got_message,
        **kwargs
    )
    while True:
        result = await inner_queue.get()
        if result[0] == "message":
            yield result[1]
        else:
            raise IOError("Channel closed", result[1])

async def connect_to_channel(pika_config: dict):
    pika_parameters = Parameters()
    for key, value in pika_config.items():
        if key == "credentials":
            value = PlainCredentials(*value)
        setattr(pika_parameters, key, value)

    connection: Connection = await asyncio_connection(pika_parameters)
    return await open_channel(connection)

# async def test_events():
#     channel = await connect_to_channel(config["pika"])
#     await queue_declare(channel,queue="sensor_events")
#     result = channel.basic_publish(
#        exchange='',
#        routing_key='sensor_events',
#        body="1234"
#     )
#     result = channel.basic_publish(
#        exchange='',
#        routing_key='sensor_events',
#        body="5678"
#     )
#
#     async for result in basic_consume(
#         channel,
#         queue = "sensor_events",
#         no_ack = True
#     ):
#         print("that "+str(result[3]))

#loop = get_event_loop()
#loop.run_until_complete(test_events())
