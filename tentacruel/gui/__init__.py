"""
General-use classes for Tentacruel TK applications

"""

# pylint: disable=invalid-name
import asyncio
from asyncio import create_task, Task
from tkinter import Frame
from typing import Any, Coroutine, Callable

from tentacruel import keep, discard

# pylint: disable=too-few-public-methods
class STAR():
    """
    When used as a column width,  STAR() expands to fill 100% of the space
    """

# pylint: disable=too-many-ancestors
class ManagedGridFrame(Frame):
    """
    Container to simplify laying out TK components in a grid

    """
    def __init__(
            self,
            master=None,
            cnf: dict = None,
            columns: int = 4,
            **kw
        ):
        """
        Container for laying out TK components in a grid that unifies configuation
        pf the widget and the relationship of a widget to the grid

        :param master: Master TK component this connected to
        :param cnf:  configuration dictionary passed onto parent Frame
        :param columns: number of internal columns
        :param kw: arbitrary keyword arguments are forwarded to parent constructor
        """
        if not cnf:
            cnf = {}
        Frame.__init__(self, master, cnf, **kw)
        self._columns = columns
        self._col = 0
        self._row = 0
        self._widgets = {}
        self.grid()

    # pylint: disable=no-self-use
    def task(self, that: Coroutine) -> Callable[..., Task]:
        """
        Create a function which wraps ``that`` and schedules it to run asynchronously

        :param that: a coroutine
        :return: a function which passes arbitrary positional and keyword parameters to ``that``
                 and schedules it to run on the event loop
        """
        def wrapper(*args, **kwargs):
            return create_task(that(*args, **kwargs))

        return wrapper

    def _clear_all(self) -> None:
        """
        Remove all widgets from grid and start fresh.

        :return:
        """
        for widget in self.grid_slaves():
            widget.destroy()
        self._col = 0
        self._row = 0
        self._widgets = {}

    def _add(self, name: str, widget_type: Callable, *args, **kwargs):
        """
        Add a widget to the user interface.  Keyword arguments that describe a position in the
        grid,  specifically::

           {"column", "columnspan", "row", "rowspan", "sticky"}

        are passed as parameters are removed from the positional and keyword argument lists
        for the widget_type and used as arguments to ``widget.grid``;  if `column` and `row`
        are not specified for a given widget,  the column and row will proceed in row-major
        order,  respecting the "columnspan"

        :param name:
        :param widget_type:
        :param args:
        :param kwargs:
        :return:
        """
        grid_args = {"column", "columnspan", "row", "rowspan", "sticky"}
        gridkw = keep(kwargs, grid_args)
        if "columnspan" in gridkw and isinstance(gridkw["columnspan"], STAR):
            gridkw["columnspan"] = self._columns

        if "column" not in gridkw and "row" not in gridkw:
            gridkw["column"] = self._col
            gridkw["row"] = self._row
            self._col += gridkw.get("columnspan", 1)
            if self._col >= self._columns:
                self._col = 0
                self._row += 1

        widgetkw = discard(kwargs, grid_args)
        widget = widget_type(self, *args, **widgetkw)
        widget.grid(**gridkw)
        self._widgets[name] = (widget)
        return widget

    def __getitem__(self, name: str):
        """

        :param name: string name of a widget
        :return: the named widget or
        :raises: ``KeyError`` if there is no widget named ``name``
        """
        return self._widgets[name]
