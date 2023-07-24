# -*- coding: utf-8 -*-
class SckSingleton(object):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(SckSingleton, cls).__new__(cls)
        return cls.instance
