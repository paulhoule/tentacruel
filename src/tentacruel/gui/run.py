import tkinter as tk
import tkinter.ttk as ttk

import asyncio
from math import floor

from tentacruel import HeosClientProtocol, RECEIVER_IP, HEOS_PORT

#
# constant widget names
#
from tentacruel.gui.browser import SourceBrowser, GeneralBrowser

MUTE = "mute"
PLAY_BUTTON = "play_button"
BROWSE_BUTTON = "browse_button"
PROGRESS = "progress"
ARTIST = "artist"
ALBUM = "album"
SONG = "song"
NOW_PLAYING = "now_playing"
STATUS = "status"
LABEL = "label"
VOLUME = "volume"
DEVICE_SELECTOR = "device_selector"
QUIT_BUTTON = "quit_button"


class Application(tk.Frame):
    def _add(self,name,widget_type,*args,**kwargs):
        widget = widget_type(self,*args,**kwargs)
        widget.grid()
        self._widgets[name]=(widget)

    def __getitem__(self,name):
        return self._widgets[name]

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.alive = True
        self.grid()
        self._widgets={}
        self.browsers = {}
        self._add(QUIT_BUTTON, tk.Button, text="Quit", command=self.quit, width=50, height=1)
        self._add(BROWSE_BUTTON, tk.Button, text="Browse", command=self.browse, width=50, height=1)
        self._add(DEVICE_SELECTOR, tk.Spinbox, command=self.task(self.select_device))
        self._add(LABEL, tk.Label, text="", width=50, height=1)
        self._add(STATUS, tk.Label, text="ok", width=50, background="green", foreground="white")
        self._add(NOW_PLAYING, tk.Label, text="*** now playing ***", width=50, height=1,
                  background="black", foreground="white")
        self._add(SONG, tk.Label, text="", width=50, height=1)
        self._add(ALBUM, tk.Label, text="", width=50, height=1)
        self._add(ARTIST, tk.Label, text="", width=50, height=1)
        self._add(PROGRESS, tk.Label, text="", width=50, height=1)
        self._add(PLAY_BUTTON, tk.Button, text="Play", width=50, height=1,
                  command=self.task(self.play_command))
        self._add(VOLUME,
                  tk.Scale, from_=0, to=100.0, length = 200,
                  command = self.task(self.set_volume),
                  orient=tk.HORIZONTAL)
        self.mute_status = tk.IntVar()
        self._add(MUTE, tk.Checkbutton,
                  command=self.task(self.set_mute),
                  text = "Mute",
                  variable = self.mute_status)

    def browse(self,sid=None,cid=None):
        if (sid,cid) in self.browsers:
            self.browsers[sid,cid].lift()
        else:
            browser = self.create_browser(sid, cid)
            self.browsers[sid,cid] = browser
            asyncio.create_task(browser.fill_source())

    def unregister_browser(self,sid, cid):
        del self.browsers[sid,cid]

    def create_browser(self, sid, cid):
        if not (sid or cid):
            return SourceBrowser(master=self, width=500, height=100)
        else:
            return GeneralBrowser(sid,cid,master=self, width=500, height=100)

    def quit(self):
        self.alive = False
        super().quit()

    def task(self,that):
        def wrapper(*args,**kwargs):
            asyncio.create_task(that(*args,**kwargs))

        return wrapper

    #
    # handle events from the system we're controlling
    #

    async def comms_up(self,hcp):
        print("in comms_up")
        self.hcp = hcp
        self.hcp.add_listener(self._handle_event)
        self.hcp.add_progress_listener(self._handle_progress)
        players = hcp.get_players()
        self[DEVICE_SELECTOR]["values"] = tuple(player["name"] for player in players)
        await self.select_device()

    def _handle_event(self,event,message):
        if event=="/player_state_changed":
            self.handle_state_changed(message)
        elif event == "/player_volume_changed":
            self.handle_volume_changed(message)
        elif event == "/player_playback_error":
            self.handle_playback_error(message)
        elif event == "/player_now_playing_changed":
            asyncio.create_task(self.handle_now_playing_changed(message))
        elif event == "/player_now_playing_progress":
            self.handle_now_playing_progress(message)
        else:
            print("received event "+str(event))

    def wrong_pid(self,message):
        that_pid = int(message["pid"])
        my_pid = int(self._current_player_info()["pid"])
        return (that_pid != my_pid)

    def handle_state_changed(self, message):
        if self.wrong_pid(message):
            return
        self[PLAY_BUTTON]["text"] = "Stop" if message["state"] == 'play' else "Play"
        if message["state"] == 'play':
            self.update_status("ok")

    def handle_volume_changed(self, message):
        if self.wrong_pid(message):
            return

        self[VOLUME].set(message["level"])
        self.mute_status.set(1 if message["mute"] == 'on' else 0)

    def handle_playback_error(self, message):
        if self.wrong_pid(message):
            return
        self.update_status("error")
        print(message)

    def _handle_progress(self, count):
        print(f"In flight command count is {count}")
        if count==0:
            self.update_status("ok")
        else:
            self.update_status("wait")

    async def handle_now_playing_changed(self, message):
        if self.wrong_pid(message):
            return

        player = self._player()
        media = await player.get_now_playing_media()
        self.now_playing = media["payload"]
        self.update_now_playing()

    def handle_now_playing_progress(self, message):
        if self.wrong_pid(message):
            return

        cur_pos = self.to_min_sec(message["cur_pos"])
        duration = self.to_min_sec(message["duration"])
        self[PROGRESS]["text"] = f"{cur_pos} / {duration}"

    def to_min_sec(self,millisec):
        sec = float(millisec) / 1000.0
        min = floor(sec / 60)
        sec = sec - 60 * min
        return f"{min}:{sec}"


    async def select_device(self):
        print("in select_device")
        player_info = self._current_player_info()
        self[LABEL]["text"] = player_info["model"]
        await self.update_player()

    async def play_command(self):
        player = self._player()
        new_state = self[PLAY_BUTTON]["text"].lower()
        await player.set_play_state(new_state)

    async def set_volume(self,level):
        volume = self[VOLUME].get()
        await self._player().set_volume(volume)

    async def set_mute(self):
        await self._player().set_mute(state = "on" if self.mute_status.get() else "off")

    def _player(self):
        return self.hcp.players[self[DEVICE_SELECTOR].get()]

    def _current_player_info(self):
        player = self[DEVICE_SELECTOR].get()
        return [x for x in self.hcp.get_players() if x["name"] == player][0]

    #
    # updaters update the GUI
    #

    def update_status(self,is_ok):
        if is_ok=="ok":
            self[STATUS]["text"]="ok"
            self[STATUS]["background"]="green"
        elif is_ok=="wait":
            self[STATUS]["text"]="waiting"
            self[STATUS]["background"]="yellow"
        else:
            self[STATUS]["text"]="error"
            self[STATUS]["background"]="red"

    async def update_player(self):
        player = self._player()
        state = (await player.get_play_state())['state']
        self[PLAY_BUTTON]["text"] = "Stop" if state=='play' else "Play"
        volume = (await player.get_volume())["level"]
        self[VOLUME].set(volume)
        mute = (await player.get_mute())["state"]
        self.mute_status.set(mute)

    def update_now_playing(self):
        self[SONG]["text"]=self.now_playing["song"]
        self[ARTIST]["text"]=self.now_playing["artist"]
        self[ALBUM]["text"]=self.now_playing["album"]

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
    global app
    hcp = HeosClientProtocol(asyncio.get_event_loop(), halt=False, start_action=app.comms_up)
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
