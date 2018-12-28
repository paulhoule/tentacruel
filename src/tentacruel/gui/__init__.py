from tkinter import Frame

# see https://docs.arangodb.com/3.4/AQL/Functions/Document.html#keep
from typing import Dict, Set


def keep(source:Dict,keep_keys: Set):
    return {key: value for (key,value) in source.items() if key in keep_keys}

def discard(source:Dict,discard_keys: Set):
    return {key: value for (key,value) in source.items() if key not in discard_keys}

class STAR():
    pass

class ManagedGridFrame(Frame):
    def __init__(
        self,
        master=None,
        cnf={},
        columns = 4,
    **kw):
        Frame.__init__(master,cnf,**kw)
        self._columns = columns
        self._col=0
        self._row=0
        self._widgets = {}
        self.grid()

    def _add(self,name,widget_type,*args,**kwargs):
        grid_args = {"column","columnspan","row","rowspan"}
        gridkw = keep(kwargs,grid_args)
        if "columnspan" in gridkw and type(gridkw["columnspan"]) == STAR:
            gridkw["columnspan"] = self._columns

        if "column" not in gridkw and "row" not in gridkw:
            gridkw["column"] = self._col
            gridkw["row"] = self._row
            self._col += gridkw.get("columnspan",1)
            if self._col >= self._columns:
                self._col = 0
                self._row += 1

        widgetkw = discard(kwargs,grid_args)
        widget = widget_type(self,*args,**widgetkw)
        widget.grid(**gridkw)
        self._widgets[name]=(widget)

    def __getitem__(self,name):
        return self._widgets[name]





