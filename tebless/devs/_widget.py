# Copyright (c) 2017 Michel Betancourt
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import logging
from functools import partial
from copy import copy
from events import Events
from blessed import Terminal
from tebless.utils import Store, dict_diff
from tebless.devs import echo, Debug

class Widget(object):
    """Widget BaseClass.

    """
    def __init__(self, cordx=0, cordy=0, width=20, height=1, **kwargs):
        self._cordx = round(cordx)
        self._cordy = round(cordy)
        self._width = round(width)
        self._height = round(height)
        self._parent = kwargs.get('parent', None)
        self._term = Terminal()

        if self._parent:
            self._store = self._parent.store
        else:
            self._store = kwargs.get('store', Store())
        self.ref = kwargs.get('ref', None)

        self._events = Events()
        events_init = filter(lambda x: x[0].startswith('on_'), kwargs.items())
        for event_name, callback in events_init:
            evt = self._events.__getattr__(event_name)
            evt += self._debug_events
            evt += callback
            self.__dict__[event_name] = evt

    def paint(self):
        raise NotImplementedError("All child class of widget need implement _paint method")

    def destroy(self):
        line = (' ' * self.width) + '\n'
        lines = line * self.height
        echo(self.term.move(self.y, self.x) + lines)

    def on_change(self, *args, **kwargs):
        self.destroy()
        self.paint()

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        elif name.startswith('on_'):
            evt = self._events.__getattr__(name)

            evt += self._debug_events
            self.__dict__[name] = evt
            return evt
        else:
            raise AttributeError(f'{self} object has no attribute {name}')
    
    def _debug_events(self, *args, **kwargs):
        pass
    
    @property
    def term(self):
        return self._term

    @property
    def store(self):
        return self._store

    @store.setter
    def store(self, value):
        self._store = value

    @property
    def x(self):
        return self._cordx

    @property
    def y(self):
        return self._cordy

    @property
    def height(self):
        """ Height of window. """
        return self._height

    @property
    def width(self):
        """ Width of window. """
        return self._width

    def __str__(self):
        return self.__class__.__name__
