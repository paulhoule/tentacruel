import tkinter as tk
import asyncio
from functools import wraps

from tentacruel import HeosClientProtocol, RECEIVER_IP, HEOS_PORT


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.alive = True
        self.grid()
        self.quit_button = tk.Button(self,text="Quit",command=self.quit,width=50,height=1)
        self.quit_button.grid()
        self.go_button = tk.Button(self,text="Go",command=self.go,width=50,height=1)
        self.go_button.grid()
        self.label = tk.Label(self,text="...",width=50,height=5)
        self.label.grid()

    def quit(self):
        self.alive = False
        super().quit()

    def go(self):
        asyncio.create_task(self._go())

    async def _go(self):
        players = await hcp.player.get_players()
        self.label["text"] = players[0]["name"]
        print(players)

async def run_tk(root, interval=0.05):
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

async def gui_thread():
    await run_tk(app)

def start_hcp():
    global hcp
    hcp = HeosClientProtocol(asyncio.get_event_loop(), halt=False)
    return hcp

async def main():
    coro = asyncio.get_event_loop().create_connection(
        start_hcp,
        RECEIVER_IP, HEOS_PORT
    )
    await asyncio.gather(gui_thread(),coro)

app = Application()
app.title = "Never lock up!"
asyncio.run(main())
