#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plex-ListDocAttrs is used during development of PlexAPI.
Example usage: AttDS(dict or object).write()
"""
import re
from collections import OrderedDict


def type_finder(s):
    type_string = str(type(s))
    x = re.search("'(.+)'", type_string)
    if x:
        return x.group(1)
    return ''


class AttDS:
    """ Helper that prints docstring attrs. """

    def __init__(self, o, keys=None, style='google'):
        self.__o = o
        if not isinstance(o, dict):
            self.o = o.__dict__.items()
            self._as_dict = o.__dict__
        else:
            self.o = o.items()
            self._as_dict = o
        if keys is None:
            self.keys = self._as_dict.keys()
        else:
            self.keys = keys
        if style == 'google':
            self.template = '%s (%s): %s'
        self.res_dict = OrderedDict()
        self.parse()

    def parse(self):
        for k, v in sorted(self.o, key=lambda k: k[0]):
            if self.keys:
                ds = ''
                for key in self.keys:
                    ds += '%s=%s ' % (key, self._as_dict.get(key, ''))
            else:
                ds = ''
            self.res_dict[k] = self.template % (k, type_finder(v), ds)

    def write(self):
        for k, v in self.res_dict.items():
            print(v)
