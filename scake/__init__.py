# -*- coding: utf-8 -*-

__version__ = "0.1.0"

from .AutoInit import AutoInit

def setup(classes_dict):
    AutoInit.update_classes_dict(new_classes_dict=classes_dict)
