# -*- coding: utf-8 -*-


class Scake():
    CLASSES_DICT = globals()

    @staticmethod
    def app(classes=None):
        if classes is not None:
            Scake.CLASSES_DICT.update(classes)
        pass
