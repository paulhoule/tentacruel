import asyncio
import json
import tkinter as tk
from typing import Dict, Set

HEADER = "header"
def LINE(number):
    return f"line{number}"

def keep(source:Dict,keep_keys: Set):
    return {key: value for (key,value) in source.items() if key in keep_keys}

class SourceBrowser(tk.Toplevel):
    def _add(self,name,widget_type,*args,**kwargs):
        widget = widget_type(self,*args,**kwargs)
        widget.grid()
        self._widgets[name]=(widget)

    def __getitem__(self,name):
        return self._widgets[name]

    def task(self,that):
        def wrapper(*args,**kwargs):
            asyncio.create_task(that(*args,**kwargs))

        return wrapper

    def heos(self):
        return self.master.hcp

    def __init__(self, heos=None, **kwargs):
        tk.Toplevel.__init__(self, **kwargs)
        self._widgets={}
        self.grid()
        self._add(HEADER, tk.Label, text="Music Sources", width=100, height=1)
        self.lift()

    async def fill_source(self):
        sources = await self.heos().browse.get_music_sources()
        services = [source for source in sources if source["type"]=="heos_server"]
        sources2 = await self.heos().browse.browse(sid=services[0]["sid"])
        sources3 = await self.heos().browse.browse(sid=1027)
        print(sources3)
        available_sources = [source for source in sources if
                             source["available"]=="true" and source["type"]!="heos_server"]
        available_sources += sources2["payload"]
        available_sources += sources3["payload"]

        print(json.dumps(available_sources,indent=2))
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
            self.master.browse(sid)

        return click_handler

    def destroy(self):
        self.master.unregister_browser(None,None)
        super().destroy()

class GeneralBrowser(tk.Toplevel):
    def _add(self,name,widget_type,*args,**kwargs):
        widget = widget_type(self,*args,**kwargs)
        widget.grid()
        self._widgets[name]=(widget)

    def __getitem__(self,name):
        return self._widgets[name]

    def task(self,that):
        def wrapper(*args,**kwargs):
            asyncio.create_task(that(*args,**kwargs))

        return wrapper

    def heos(self):
        return self.master.hcp

    def __init__(self, sid, cid, **kwargs):
        tk.Toplevel.__init__(self, **kwargs)
        self.coordinates = {}
        if sid:
            self.coordinates["sid"]=sid
        if cid:
            self.coordinates["cid"]=cid

        self._widgets={}
        self.grid()
        self._add(HEADER, tk.Label, text="Music Sources", width=100, height=1)
        self.lift()

    async def fill_source(self):
        query = self.coordinates.copy()
        if "cid" in query:
            query["range"]="0,20"
        result = await self.heos().browse.browse(**query)
        items = result["payload"]
        for i in range(len(items)):
            item = items[i]
            print(item)
            keys = keep(item,{"cid","mid"})
            keys["sid"] = self.coordinates["sid"]
            self._add(LINE(i),
                tk.Button,
                text=item["name"],
                width=100,height=1,
                bg="white" if i % 2 else "lightgrey",
                command=self.browse_to_item(**keys)
            )

    def browse_to_item(self,sid=None,cid=None,mid=None):
        def click_handler():
            self.master.browse(sid,cid)

        return click_handler



