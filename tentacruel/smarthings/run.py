from asyncio import get_event_loop, sleep

import aiohttp

import pysmartthings
from tentacruel.config import get_config
from tentacruel.pinger import ensure_proactor

config = get_config()
token = config["smartthings"]["personal_access_token"]

async def amain():
    async with aiohttp.ClientSession() as session:
        api = pysmartthings.SmartThings(session, token)
        devices = {d.name:d for d in await api.devices() }
        linda = devices['Linda (Wemo)']
        for x in range(10):
            await sleep(5)
            await linda.command('main', 'switch', 'on')
            await sleep(5)
            await linda.command('main','switch','off')

if __name__ == "__main__":
    ensure_proactor()
    loop = get_event_loop()
    loop.run_until_complete(amain())