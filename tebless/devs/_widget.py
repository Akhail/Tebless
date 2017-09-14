# Copyright (c) 2017 Michel Betancourt
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import logging

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

        def on_change_debug(*_):
            """ changes debug """
            if Debug.is_active:
                _copy = copy(self.__dict__)
                del _copy['_previous_state']

                msg = dict_diff(self._previous_state, _copy)
                with Debug(self):
                    Debug.log('Change', msg)

                self._previous_state = _copy

            self.destroy()
            self.paint()

        events = Events()

        self.on_change = events.on_change
        self.on_enter = events.on_enter
        self.on_key_arrow = events.on_key_arrow
        self.on_exit = events.on_exit
        self.on_key = events.on_key

        self.on_change += on_change_debug

        events = filter(lambda item: 'on_' in item[0], kwargs.items())
        events = dict(events)
        if Debug.is_active:
            with Debug(self):
                params = filter(lambda item: 'on_' not in item[0], kwargs.items())
                params = dict(params)
                params.update(dict(
                    cordx=self._cordx,
                    cordy=self._cordy,
                    width=self._width,
                    height=self._height
                ))
                Debug.log('Create', params)
                Debug.log('Events', events)

        for key, event in events.items():
            if key == 'on_enter':
                self.on_enter += lambda fn=event, *args, **kwargs: fn(self, *args, **kwargs)
            elif key == 'on_key_arrow':
                self.on_key_arrow += lambda fn=event, *args, **kwargs: fn(self, *args, **kwargs)
            elif key == 'on_exit':
                self.on_exit += lambda fn=event, *args, **kwargs: fn(self, *args, **kwargs)
            elif key == 'on_key':
                self.on_key += lambda fn=event, *args, **kwargs: fn(self, *args, **kwargs)
            elif key == 'on_change':
                self.on_change += lambda fn=event, *args, **kwargs: fn(self, *args, **kwargs)
        self.update()

    def paint(self):
        raise NotImplementedError("All child class of widget need implement _paint method")

    def destroy(self):
        line = (' ' * self.width) + '\n'
        lines = line * self.height
        echo(self.term.move(self.y, self.x) + lines)

    def update(self):
        if Debug.is_active:
            _copy = copy(self.__dict__)
            if '_previous_state' in _copy:
                del _copy['_previous_state']
            self._previous_state = _copy

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

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