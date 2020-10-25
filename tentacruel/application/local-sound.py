from asyncio import get_event_loop
import json
import aiohttp

from tentacruel.pinger import ensure_proactor

HEOS_GATEWAY = "http://192.168.0.21:9617"

async def amain():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('http://192.168.0.21:9617/heos') as socket:
            GET_PLAYERS = {"command":"player/get_players","parameters":{},"requestId":"2cc86994-73fa-4283-91b6-a42d93a6ee15"}
            await socket.send_str(json.dumps(GET_PLAYERS))
            reply = json.loads(await socket.receive_str())
            LIVING_ROOM = [line for line in reply["message"] if line["name"] == 'Living Room'][0]['pid']
            print(LIVING_ROOM)
            


if __name__ == "__main__":
    ensure_proactor()
    loop = get_event_loop()
    loop.run_until_complete(amain())
