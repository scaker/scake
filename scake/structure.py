# -*- coding: utf-8 -*-


class ScakeDict(dict):
    def __getattr__(self, key):
        return self.get(key, None)
