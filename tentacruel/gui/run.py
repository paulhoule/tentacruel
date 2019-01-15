import tkinter as tk

import asyncio
import json
from logging import getLogger, DEBUG, StreamHandler
from math import floor

from tentacruel import HeosClientProtocol, RECEIVER_IP, HEOS_PORT
from tentacruel.gui import ManagedGridFrame
from tentacruel.gui.browser import SourceBrowser, GeneralBrowser, wrap_window, PlaylistBrowser, wrap_scrollbar

logger = getLogger(__name__)
#getLogger(None).setLevel(DEBUG)
getLogger(None).addHandler(StreamHandler())

#
# constant widget names
#


MUTE = "mute"
PLAY_BUTTON = "play_button"
PREV_BUTTON = "prev_button"
NEXT_BUTTON = "next_button"
BROWSE_BUTTON = "browse_button"
PLAYLIST_BUTTON = "playlist_button"
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


class Application(ManagedGridFrame):

    def __init__(self, master=None):
        super().__init__(master)
        self.alive = True
        self.browsers = {}
        self.queues = {}
        self._transitioning_to = None

        self._add(QUIT_BUTTON, tk.Button, text="Quit", command=self.quit, width=15, height=1,
                  columnspan=1)
        self._add(DEVICE_SELECTOR, tk.Spinbox, command=self.task(self.select_device),
                  columnspan=2)
        self._add(BROWSE_BUTTON, tk.Button, text="Browse", command=self.browse, width=15, height=1,
                  columnspan=1)

        self._add(LABEL, tk.Label, text="", width=50, height=1,columnspan=3)
        self._add(PLAYLIST_BUTTON, tk.Button, text="Playlist", width=15, height=1, columnspan=1
                  ,command=self.playlist)
        self._add(STATUS, tk.Label, text="ok", width=50, background="green", foreground="white",
                  columnspan=4)
        self._add(SONG+"_label", tk.Label,text="Song:",width=15,anchor='e')
        self._add(SONG, tk.Label, text="", width=50, height=1,columnspan=3,anchor='w')
        self._add(ALBUM+"_label", tk.Label,text="Album:",width=15,anchor='e')
        self._add(ALBUM, tk.Label, text="", width=50, height=1,columnspan=3,anchor='w')
        self._add(ARTIST+"_label", tk.Label,text="Artist:",width=15,anchor='e')
        self._add(ARTIST, tk.Label, text="", width=50, height=1,columnspan=3,anchor='w')
        self._add(PROGRESS, tk.Label, text="", width=50, height=1,columnspan=4)
        self._add(PREV_BUTTON, tk.Button, text="Prev", width=15, height=1,command=self.task(self.prev))
        self._add(PLAY_BUTTON, tk.Button, text="Play", width=30, height=1,
                  columnspan=2,
                   command=self.task(self.play_command))
        self._add(NEXT_BUTTON, tk.Button, text="Next", width=15, height=1,command=self.task(self.next))
        self._add(VOLUME,
                  tk.Scale, from_=0, to=100.0, length = 200,
                  command = self.task(self.set_volume),
                  columnspan=4,
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

    def playlist(self):
        my_pid = int(self._current_player_info()["pid"])
        playlist = wrap_window(self,PlaylistBrowser,frame_arguments={"pid": my_pid},width=500, height=100)
        self.queues[my_pid]=playlist
        asyncio.create_task(playlist.fill_source())

    def unregister_browser(self,sid, cid):
        del self.browsers[sid,cid]

    def create_browser(self, sid, cid):
        if not (sid or cid):
            return wrap_window(self,SourceBrowser,width=500, height=100)
        else:
            return wrap_scrollbar(self,GeneralBrowser,
                               frame_arguments={
                                   "sid": sid,
                                   "cid": cid
                               },
                               width=500, height=100)

    async def play_item(self,sid=None,cid=None,mid=None):
        identifiers = {}
        if sid:
            identifiers["sid"] = sid
        if cid:
            identifiers["cid"] = cid
        if mid:
            identifiers["mid"] = mid
        await self._player().add_to_queue(sid,cid,mid)

    async def play_queue(self, qid=None, pid=None):
        await self._player().play_queue(qid,pid)

    async def remove_from_queue(self,qid=None,pid=None):
        await self._player().remove_from_queue(qid,pid)

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
        logger.debug("in comms_up")
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
        elif event == "/player_queue_changed":
            self.handle_player_queue_changed(message)
        else:
            logger.warning("received unhandled event %s",event)

    def wrong_pid(self,message):
        that_pid = int(message["pid"])
        my_pid = int(self._current_player_info()["pid"])
        return (that_pid != my_pid)

    def handle_state_changed(self, message):
        if self.wrong_pid(message):
            return
        self._transitioning_to = None
        self[PLAY_BUTTON]["text"] = "Stop" if message["state"] == 'play' else "Play"
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
        logger.error(message)

    def handle_player_queue_changed(self, message):
        pid = int(message["pid"])
        if pid in self.queues:
            logger.warning(f"Filling queue for player {pid}")
            queue = self.queues[pid]
            asyncio.create_task(queue.fill_source())
        else:
            logger.warning(f"Could not fill queue for {pid}")
            logger.warning(f"Queue keys: {self.queues.keys()}")


    def _handle_progress(self, count):
        logger.debug(f"In flight command count is %s",count)
        if count==0:
            self.update_status("ok" if self._transitioning_to == None else "starting")
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
        logger.debug("in select_device")
        player_info = self._current_player_info()
        self[LABEL]["text"] = player_info["model"]
        await self.update_player()

    async def play_command(self):
        player = self._player()
        new_state = self[PLAY_BUTTON]["text"].lower()
        self._transitioning_to = new_state
        await player.set_play_state(new_state)

    async def set_volume(self,level):
        volume = self[VOLUME].get()
        await self._player().set_volume(volume)

    async def set_mute(self):
        await self._player().set_mute(state = "on" if self.mute_status.get() else "off")

    async def next(self):
        self._transitioning_to = "play"
        await self._player().play_next()

    async def prev(self):
        self._transitioning_to = "play"
        await self._player().play_previous()

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
        elif is_ok=="starting":
            self[STATUS]["text"]="starting"
            self[STATUS]["background"]="orange"
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
        my_pid = int(self._current_player_info()["pid"])
        if my_pid in self.queues:
            queue = self.queues[my_pid]
            queue.set_current_song(self.now_playing["qid"])

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
