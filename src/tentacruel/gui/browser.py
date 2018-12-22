import asyncio
import json
import tkinter as tk

HEADER = "header"
def LINE(number):
    return f"line{number}"

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

    def __init__(self, heos=None, **kwargs):
        tk.Toplevel.__init__(self, **kwargs)
        self.heos = heos
        self._widgets={}
        self.grid()
        self._add(HEADER, tk.Label, text="Music Sources", width=100, height=1)
        self.lift()

    async def fill_source(self):
        sources = await self.heos.browse.get_music_sources()
        services = [source for source in sources if source["type"]=="heos_server"]
        sources2 = await self.heos.browse.browse(sid=services[0]["sid"])
        sources3 = await self.heos.browse.browse(sid=1027)
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
            browser = GeneralBrowser(master=self, heos=self.heos, width=500, height=100)
            asyncio.create_task(browser.fill_source(sid=sid))

        return click_handler

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

    def __init__(self, heos=None, **kwargs):
        tk.Toplevel.__init__(self, **kwargs)
        self.heos = heos
        self._widgets={}
        self.grid()
        self._add(HEADER, tk.Label, text="Music Sources", width=100, height=1)
        self.lift()

    async def fill_source(self,**kwargs):
        result = await self.heos.browse.browse(**kwargs)
        sid = kwargs["sid"]
        items = result["payload"]
        for i in range(len(items)):
            item = items[i]
            self._add(LINE(i),
                tk.Button,
                text=item["name"],
                width=100,height=1,
                bg="white" if i % 2 else "lightgrey",
                command=self.browse_to_item(sid=sid,cid=item["cid"])
            )

    def browse_to_item(self,**kwargs):
        def click_handler():
            browser = GeneralBrowser(master=self, heos=self.heos, width=500, height=100)
            asyncio.create_task(browser.fill_source(**kwargs))

        return click_handler



