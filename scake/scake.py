# -*- coding: utf-8 -*-


class Scake():
    CLASSES_DICT = globals()
    GENERATED_SCAKE_PACKAGES_NAME = 'scake_packages'
    GENERATED_SCAKE_CLASS_NAME_FORMAT = '%(class_name)s_'
    GENERATED_SCAKE_CLASS_CODE = """\n
class %(scake_class_name)s():
    def __init__(self, %(init_params)s):
%(assign_params)s

    def __call__(self):
        pass
    """

    @staticmethod
    def app(classes=None):
        if classes is not None:
            Scake.CLASSES_DICT.update(classes)
        pass
