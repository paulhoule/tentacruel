import tkinter as tk
import asyncio
from functools import wraps
from math import floor

from tentacruel import HeosClientProtocol, RECEIVER_IP, HEOS_PORT


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
        self._add("quit_button",tk.Button,text="Quit",command=self.quit,width=50,height=1)
        self._add("device_selector",tk.Spinbox,command=self.task(self.select_device))
        self._add("label",tk.Label,text="",width=50,height=1)
        self._add("now_playing", tk.Label, text="*** now playing ***", width=50, height=1,
                  background="black",foreground="white")
        self._add("song",tk.Label,text="",width=50,height=1)
        self._add("album",tk.Label,text="",width=50,height=1)
        self._add("artist",tk.Label,text="",width=50,height=1)
        self._add("progress",tk.Label,text="",width=50,height=1)
        self._add("play_button", tk.Button, text="Play", width=50, height=1,
                  command=self.task(self.play_command))
        self._add("volume",
                  tk.Scale, from_=0, to=100.0, length = 200,
                  command = self.task(self.set_volume),
                  orient=tk.HORIZONTAL)

    def quit(self):
        self.alive = False
        super().quit()

    def task(self,that):
        def wrapper(*args,**kwargs):
            asyncio.create_task(that(*args,**kwargs))

        return wrapper

    def _handle_event(self,event,message):
        if event=="/player_state_changed":
            self._handle_state_changed(message)
        elif event == "/player_volume_changed":
            self._handle_volume_changed(message)
        elif event == "/player_playback_error":
            self._handle_playback_error(message)
        elif event == "/player_now_playing_changed":
            asyncio.create_task(self._handle_now_playing_changed(message))
        elif event == "/player_now_playing_progress":
            self._handle_now_playing_progress(message)
        else:
            print("received event "+str(event))

    def wrong_pid(self,message):
        that_pid = int(message["pid"])
        my_pid = int(self._current_player_info()["pid"])
        return (that_pid != my_pid)

    def _handle_state_changed(self,message):
        if self.wrong_pid(message):
            return

        self["play_button"]["text"] = "Stop" if message["state"] == 'play' else "Play"

    def _handle_volume_changed(self,message):
        if self.wrong_pid(message):
            return

        self["volume"].set(message["level"])

    def _handle_playback_error(self,message):
        if self.wrong_pid(message):
            return

        print(message)

    async def _handle_now_playing_changed(self,message):
        if self.wrong_pid(message):
            return

        player = self._player()
        media = await player.get_now_playing_media()
        self.now_playing = media["payload"]
        self._update_now_playing()

    def _handle_now_playing_progress(self,message):
        if self.wrong_pid(message):
            return

        cur_pos = self.to_min_sec(message["cur_pos"])
        duration = self.to_min_sec(message["duration"])
        self["progress"]["text"] = f"{cur_pos} / {duration}"

    def to_min_sec(self,millisec):
        sec = float(millisec) / 1000.0
        min = floor(sec / 60)
        sec = sec - 60 * min
        return f"{min}:{sec}"

    def _update_now_playing(self):
        self["song"]["text"]=self.now_playing["song"]
        self["artist"]["text"]=self.now_playing["artist"]
        self["album"]["text"]=self.now_playing["album"]

    async def comms_up(self,hcp):
        print("in comms_up")
        self.hcp = hcp
        self.hcp.add_listener(self._handle_event)
        players = hcp.get_players()
        self["device_selector"]["values"] = tuple(player["name"] for player in players)
        await self.select_device()

    async def select_device(self):
        print("in select_device")
        player_info = self._current_player_info()
        self["label"]["text"] = player_info["model"]
        await self._update_player()

    async def _update_player(self):
        player = self._player()
        state = (await player.get_play_state())['state']
        self["play_button"]["text"] = "Stop" if state=='play' else "Play"
        volume = (await player.get_volume())["level"]
        self["volume"].set(volume)

    async def play_command(self):
        player = self._player()
        new_state = self["play_button"]["text"].lower()
        await player.set_play_state(new_state)

    async def set_volume(self,level):
        print(level)
        volume = self["volume"].get()
        await self._player().set_volume(volume)

    def _player(self):
        return self.hcp.players[self["device_selector"].get()]

    def _current_player_info(self):
        player = self["device_selector"].get()
        return [x for x in self.hcp.get_players() if x["name"] == player][0]

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
