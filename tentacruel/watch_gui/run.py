"""

GUI application to watch system status.

"""
import asyncio
from asyncio import run
from logging import getLogger, StreamHandler
from os import environ

from tentacruel.config import get_config
from tentacruel.gui import ManagedGridFrame

LOGGER = getLogger(__name__)

# pylint: disable=invalid-name
async def run_tk(root, interval=0.05, tk=None) -> None:
    '''
    Run a tkinter app in an asyncio event loop.
    '''
    try:
        while root.alive:
            root.update()
            await asyncio.sleep(interval)
    except tk.TclError as e:
        if "application has been destroyed" not in e.args[0]:
            raise

# pylint: disable=too-many-ancestors
class Application(ManagedGridFrame):
    """
    No-operation class that will become the main class of the app.


    """

    async def setup(self) -> None:
        """
        Setup stage completed asynchronously so we can use asynchronous
        facilities to do the setup

        :return:
        """

async def amain() -> None:
    """
    amain is a main method,  but it is asynchronous,  main() jumps into here
    right away where we initialize the application and then start polling
    the tk event loop to handle gui events together with asyncio

    :return:
    """
    config = get_config()
    app = Application(config)
    await app.setup()
    await run_tk(app)

async def main() -> None:
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
