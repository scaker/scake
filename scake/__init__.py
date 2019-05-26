# -*- coding: utf-8 -*-

__version__ = "0.1.0"

from .ScakeSetup import ScakeSetup
from .AutoScake import AutoScake
from .ScakeDict import ScakeDict

def setup(classes_dict=None):
    if classes_dict is not None:
        ScakeSetup.CLASSES_DICT.update(classes_dict)
    pass
