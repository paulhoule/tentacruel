"""
Pinger application.  Periodically poll hosts to see if they are up.  Log state in the
document database,  but report state changes to the message Q

"""
from asyncio import run, get_event_loop, create_task, get_running_loop

from aio_pika import ExchangeType, connect_robust
from tentacruel.config import get_config
from tentacruel.heos_watcher import HeosWatcher
from tentacruel.pinger import ensure_proactor, Pinger
from tentacruel.pinger.hue_ping import hue_loop, protect


async def pika_connect(config):
    """
    Initialization that can only be completed in an async method
    """
    connection = await connect_robust(
        loop=get_event_loop(),
        **config["pika"]
    )

    channel = await connection.channel()
    exchange = await channel.declare_exchange("smartthings", ExchangeType.FANOUT)
    return exchange

async def amain():
    """
    Asynchronous main method.

    :return:
    """
    config = get_config()
    watcher = HeosWatcher(config)
    await watcher.run()
    never = get_running_loop().create_future()
    await never


if __name__ == "__main__":
    ensure_proactor()
    run(amain())
