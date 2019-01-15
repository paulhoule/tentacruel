import asyncio
import json
import tkinter as tk
from typing import Dict, Set
from logging import getLogger

from tentacruel.gui import ManagedGridFrame, keep, discard, STAR

logger = getLogger(__name__)
HEADER = "header"
def LINE(number):
    return f"line{number}"

def LABEL(number):
    return f"label{number}"

def PLAY(number):
    return f"play{number}"

def TYPE(number):
    return f"type{number}"

def BROWSE(number):
    return f"browse{number}"


class SourceBrowser(ManagedGridFrame):
    def heos(self):
        return self._application.hcp

    def __init__(self, master=None, application=None, **kwargs):
        super().__init__(master=master,columns=1,**kwargs)
        self._application=application
        self._add(HEADER, tk.Label, text="Music Sources", width=100, height=1)

    async def fill_source(self):
        sources = await self.heos().browse.get_music_sources()
        services = [source for source in sources if source["type"]=="heos_server"]
        sources2 = await self.heos().browse.browse(sid=services[0]["sid"])
        sources3 = await self.heos().browse.browse(sid=1027)
        available_sources = [source for source in sources if
                             source["available"]=="true" and source["type"]!="heos_server"]
        available_sources += sources2["payload"]
        available_sources += sources3["payload"]

        for i in range(len(available_sources)):
            source = available_sources[i]
            self._add(LINE(i),
                      tk.Button,
                      text=source["name"],
                      width=100,height=1,
                      bg="white" if i % 2 else "lightgrey",
                      command = self.browse_to_source(source["sid"])
            )

    def browse_to_source(self,sid):
        def click_handler():
            self._application.browse(sid)

        return click_handler

    def destroy(self):
        self._application.unregister_browser(None,None)
        super().destroy()

class GeneralBrowser(ManagedGridFrame):
    def heos(self):
        return self._application.hcp

    def __init__(self, sid, cid, application=None, **kwargs):
        super().__init__(columns=4,**kwargs)
        self._application = application
        self.coordinates = {}
        if sid:
            self.coordinates["sid"]=sid
        if cid:
            self.coordinates["cid"]=cid

        self._add(HEADER, tk.Label, text="Music Sources", width=100, height=1,columnspan=4)

    async def fill_source(self):
        query = self.coordinates.copy()
        if "cid" in query:
            query["range"]="0,20"
        result = await self.heos().browse.browse(**query)
        items = result["payload"]
        for i in range(len(items)):
            item = items[i]
            keys = keep(item,{"cid","mid"})
            keys["sid"] = self.coordinates["sid"]
            if "cid" not in keys:
                keys["cid"] = self.coordinates["cid"]

            if item.get("container","no")=="yes":
                self._add(BROWSE(i),
                    tk.Button,
                    text = "Browse",
                    command=self.browse_to_item(**keys),
                    row = i+1,
                    column = 0
                )

            if item.get("playable","no")=="yes":
                self._add(PLAY(i),
                    tk.Button,
                    command=self.play_item(**keys),
                    text="Play",
                    row=i + 1,
                    column=1
                )

            if "type" in item:
                self._add(TYPE(i),
                    tk.Label,
                    text = item["type"],
                    row=i+1,
                    column=2
                )

            self._add(LINE(i),
                tk.Button,
                text=item["name"],
                width=100,height=1,
                bg="white" if i % 2 else "lightgrey",
                command=self.browse_to_item(**keys),
                row = i+1,
                column = 3
            )

    def browse_to_item(self,sid=None,cid=None,mid=None):
        def click_handler():
            self._application.browse(sid,cid)

        return click_handler

    def play_item(self,sid=None,cid=None,mid=None):
        def click_handler():
            asyncio.create_task(self._application.play_item(sid,cid,mid))

        return click_handler

class PlaylistBrowser(ManagedGridFrame):
    def heos(self):
        return self._application.hcp

    def __init__(self, pid, application=None, **kwargs):
        super().__init__(columns=6,**kwargs)
        self._application = application
        self._pid = pid
        self._qid = None
        self._items = []
        self._rows = []
        self._add(HEADER, tk.Label, text="Playlist", width=100, height=1, columnspan=STAR())

    async def fill_source(self):
        # some details:  we should have a centrally managed now_playing rather than fetching it
        # every time4
        result = await self.heos()[self._pid].get_queue()
        now_playing = await self.heos()[self._pid].get_now_playing_media()
        self._rows.clear()
        self._clear_all()

        self._items = result["payload"]
        self._add(HEADER, tk.Label, text="Playlist", width=100, height=1,columnspan=STAR())
        for i in range(len(self._items)):
            item = self._items[i]
            self._rows.append([
                self._add(f"qid_{i}",tk.Label,text=item["qid"],sticky="ew"),
                self._add(f"play_{i}", tk.Button, text="Play", sticky="ew",
                          command = self.play_item(item["qid"])),
                self._add(f"remove_{i}", tk.Button, text="Remove", sticky="ew",
                          command=self.remove_item(item["qid"])),
                self._add(f"song_{i}",tk.Label,text=item["song"],sticky="ew"),
                self._add(f"album_{i}",tk.Label,text=item["album"],sticky="ew"),
                self._add(f"artist_{i}",tk.Label,text=item["artist"],sticky="ew")
            ])

        self.set_current_song(now_playing["payload"].get("qid",None))

    def play_item(self,qid=None):
        def click_handler():
            asyncio.create_task(self._application.play_queue(qid,self._pid))

        return click_handler

    def remove_item(self,qid=None):
        def click_handler():
            asyncio.create_task(self._application.remove_from_queue(qid,self._pid))

        return click_handler

    def set_current_song(self,qid):
        self._qid=qid

        for i in range(len(self._items)):
            if qid and i==qid-1:
                for col in self._rows[i]:
                    col["fg"] = "white"
                    col["bg"] = "darkblue"
            else:
                for col in self._rows[i]:
                    col["fg"] = "black"
                    col["bg"] = "white" if i % 2 else "lightgrey"

def wrap_window(master,inner_frame,frame_arguments={},**kwargs):
    window = tk.Toplevel(master=master,**kwargs)
    window.grid()
    that = inner_frame(master=window,application=master,**frame_arguments)
    that.grid()
    return that



