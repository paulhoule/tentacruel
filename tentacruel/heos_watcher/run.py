"""
Websocket gateway.

Convert websocket calls to calls to the HEOS server

"""
import json
from _contextvars import ContextVar
from asyncio import create_task
from logging import getLogger, StreamHandler
from os import environ
from pathlib import Path
from uuid import uuid1

import aiohttp
import yaml
from aiohttp import web
from tentacruel import HeosClientProtocol
from tentacruel.pinger import ensure_proactor

if "LOGGING_LEVEL" in environ:
    getLogger(None).setLevel(environ["LOGGING_LEVEL"])
getLogger(None).addHandler(StreamHandler())

LOG = getLogger(__name__)

# DEFINE CONTEXT VAR
REQUEST_ID = ContextVar("REQUEST_ID")

async def heos(request):
    listener_id = str(uuid1())
    LOG.debug("Starting Listener with id "+listener_id)
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async def send_event(event, message):
        packet = {"type": "event", "event": event, "message": message}
        LOG.debug("about to send "+event)
        await ws.send_str(json.dumps(packet))

    async def send_reply(response):
        packet= {
            "type": "response",
            "requestId": REQUEST_ID.get(),
            "message": response.result()
        }
        LOG.debug("replied with "+str(packet))
        await ws.send_str(json.dumps(packet))

    heos_client.add_listener(send_event)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            packet = json.loads(msg.data)
            LOG.debug("got: "+str(packet))
            reset_token = REQUEST_ID.set(packet["requestId"])
            try:
                heos_client._run_command(
                    packet["command"],
                    **packet["parameters"]
                ).add_done_callback(lambda x: create_task(send_reply(x)))
            finally:
                REQUEST_ID.reset(reset_token)
        elif msg.type == aiohttp.WSMsgType.ERROR:
            LOG.debug('ws connection closed with exception', exc_info=ws.exception())

    LOG.debug('websocket connection closed')
    heos_client.remove_listener(send_event)

    return ws

def my_listener(event, message):
    print(event, message)

async def init(that):
    await heos_client.setup()


with open(Path.home() / ".tentacruel" / "config.yaml") as a_stream:
    config = yaml.load(a_stream)

if __name__ == "__main__":
    ensure_proactor()
    app = web.Application()
    heos_client = HeosClientProtocol(config["server"]["ip"])
    app.on_startup.append(init)
    app.add_routes([web.get('/heos', heos)])
    web.run_app(app, host='localhost', port=9617)

