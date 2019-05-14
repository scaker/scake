# -*- coding: utf-8 -*-

import inspect

class AutoInit():
    CLASSES_DICT = globals()

    @staticmethod
    def update_classes_dict(new_classes_dict):
        AutoInit.CLASSES_DICT.update(new_classes_dict)

    @staticmethod
    def init(data_dict):
        # loop up in "CLASSES_DICT"
        obj_class = AutoInit.CLASSES_DICT[data_dict['class']]
        init_params = data_dict.get(data_dict['class'], {}).get('init', {})

        names, varargs, keywords, defaults = inspect.getargspec(obj_class.__init__) #ArgSpec(args=['self', 'a', 'b', 'c'], varargs=None, keywords=None, defaults=(10, ''))
        names = names[1:]
        if len(names) > len(defaults):
            # check required params
            num_required_names = len(names) - len(defaults)
            required_names = names[:num_required_names]
            for rn in required_names:
                if rn not in init_params:
                    return None

        # check for redundant keys in "init_params"
        redundant_params = {}
        redundant_keys = []
        for key in init_params.keys():
            if key not in names:
                redundant_keys.append(key)

        for key in redundant_keys:
            redundant_params[key] = init_params.pop(key)

        obj = obj_class(**init_params)

        for k, v in redundant_params.items():
            setattr(obj, k, v)

        return obj

    def __init__(self, data_dict):
        self.data_dict = data_dict        
        self.obj = AutoInit.init(data_dict)
        pass

    def get(self):
        return self.obj
