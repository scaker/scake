# -*- coding: utf-8 -*-
import inspect
from .ScakeSetup import ScakeSetup
from .ScakeDict import ScakeDict

class AutoScake():
    def __init__(self, exec_graph):
        assert isinstance(exec_graph, dict) or isinstance(exec_graph, ScakeDict)
        self.exec_graph = exec_graph
        
        parsed_dict = ScakeDict()
        for key, value in exec_graph.items():            
            if isinstance(value, dict):
                auto = AutoScake(value)
                setattr(self, key, auto.obj)
                parsed_dict[key] = auto.obj
            else:
                if isinstance(value, str) and value.startswith('scake'):
                    # todo
                    pass
                else:
                    setattr(self, key, value)
                    parsed_dict[key] = value
            
            if key in ScakeSetup.CLASSES_DICT.keys():
                parsed_dict = self.__init_instance(class_str=key, param_dict=getattr(self, key))
                break
            
            pass
        
        self.obj = parsed_dict
        pass
    
    def __init_instance(self, class_str, param_dict):
        # loop up in "CLASSES_DICT"
        obj_class = ScakeSetup.CLASSES_DICT[class_str]        
        init_params = param_dict

        #deprecated
        #names, varargs, keywords, defaults = inspect.getargspec(obj_class.__init__) #ArgSpec(args=['self', 'a', 'b', 'c'], varargs=None, keywords=None, defaults=(10, ''))
        names, varargs, keywords, defaults, kwonlyargs, kwonlydefaults, annotations = inspect.getfullargspec(obj_class.__init__) # https://docs.python.org/3.4/library/inspect.html#inspect.getfullargspec
        names = names[1:]
        defaults = [] if not defaults else defaults
        if len(names) > len(defaults):
            # check required params
            num_required_names = len(names) - len(defaults)
            required_names = names[:num_required_names]
            for rn in required_names:
                if rn not in init_params:
                    raise Exception('Missing required param "%s" of %s' % (rn, class_str))

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
        
    def get():
        return self.obj
