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

class HeosService:

    def __init__(self, config):
        self.client = HeosClientProtocol(config["server"]["ip"])

    async def setup(self, app):
        await self.client.setup()

    async def __call__(self, request):
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



        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                packet = json.loads(msg.data)
                LOG.debug("got: "+str(packet))
                reset_token = REQUEST_ID.set(packet["requestId"])
                try:
                    self.client._run_command(
                        packet["command"],
                        **packet["parameters"]
                    ).add_done_callback(lambda x: create_task(send_reply(x)))
                finally:
                    REQUEST_ID.reset(reset_token)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                LOG.debug('ws connection closed with exception', exc_info=ws.exception())

        LOG.debug('websocket connection closed')
        self.client.remove_listener(send_event)

        return ws


with open(Path.home() / ".tentacruel" / "config.yaml") as a_stream:
    config = yaml.load(a_stream)

if __name__ == "__main__":
    ensure_proactor()
    app = web.Application()
    heos = HeosService(config)
    app.on_startup.append(heos.setup)
    app.add_routes([web.get('/heos', heos)])
    web.run_app(app, host='0.0.0.0', port=9617)


