# -*- coding: utf-8 -*-

class ScakeSetup():
    CLASSES_DICT = globals()
    
    @staticmethod
    def setup(classes_dict=None):
        if classes_dict is not None:
            ScakeSetup.CLASSES_DICT.update(classes_dict)
        pass