# -*- coding: utf-8 -*-
import inspect
import sys
from scake.setup import ScakeSetup
from scake.structure import ScakeDict

class AutoScake():
    def __init__(self, exec_graph, node_path=['scake'], root=None):
        assert isinstance(exec_graph, dict) or isinstance(exec_graph, ScakeDict)
        self.exec_graph = exec_graph
        self.node_path = node_path
        self.root = root if root else self
        self.is_done_init = True
        self.wait_dict = {}
        
        parsed_dict = self.__init_exec_graph(self.exec_graph)
        
        setattr(parsed_dict, 'is_done_init', self.is_done_init)
        self.obj = parsed_dict
        
        if len(node_path) == 1 and len(self.wait_dict) > 0:
            self.__check_wait_dict_and_reinit()
        
        pass
    
    def __check_wait_dict_and_reinit(self):        
        last_length_wait_dict = len(self.wait_dict)
        while True:
            self.obj = self.__init_exec_graph(self.exec_graph)
            if len(self.wait_dict) == 0 or len(self.wait_dict) == last_length_wait_dict:
                break
            last_length_wait_dict = len(self.wait_dict)
        pass
    
    def __get_scake_component(self, component_str, root):
        nodes = component_str.split('.')[1:]
        result = None
        ptr = root
        for n in nodes:
            if hasattr(ptr, n):
                ptr = getattr(ptr, n)
            else:
                return None
        result = ptr
        return result
    
    def __init_exec_graph(self, exec_graph):
        parsed_dict = ScakeDict()
        for key, value in exec_graph.items():
            if isinstance(value, dict):
                updated_node_path = self.node_path.copy()
                updated_node_path.append(key)
                auto = AutoScake(exec_graph=value, 
                                 node_path=updated_node_path, 
                                 root=self.root)
                setattr(self, key, auto.obj)
                parsed_dict[key] = auto.obj
            else:
                if isinstance(value, str) and value.startswith('scake'):
                    if value.count('.') == 0:
                        raise Exception('Invalid reference to scake component: %s' % value)
                    component = self.__get_scake_component(component_str=value, root=self.root)
                    if component:
                        setattr(self, key, component)
                        parsed_dict[key] = component
                        self.root.wait_dict.pop(value, None)
                    else:
                        print('Component not found @', value)
                        self.is_done_init = False
                        self.root.wait_dict[value] = '.'.join(self.node_path)
                        print('self.root.wait_dict', self.root.wait_dict)
                        pass
                    pass
                else:
                    setattr(self, key, value)
                    parsed_dict[key] = value
            
            if key in ScakeSetup.CLASSES_DICT.keys():
                auto = getattr(self, key)
                if auto.is_done_init:
                    new_instance = self.__init_instance(class_str=key, param_dict=auto) # override self.obj
                    # copy all parsed_dict to the new instance
                    for pkey, pvalue in parsed_dict.items():
                        setattr(new_instance, pkey, pvalue)
                    parsed_dict = new_instance
                else:
                    print('** Component not found @', value)
                    self.is_done_init = False
                    ##self.root.wait_dict[value] = '.'.join(node_path)
                    print('self.root.wait_dict', self.root.wait_dict)
                    pass
                break            
            pass
        return parsed_dict
    
    def __init_instance(self, class_str, param_dict):
        # loop up in "CLASSES_DICT"
        obj_class = ScakeSetup.CLASSES_DICT[class_str]        
        init_params = param_dict
        
        major, minor, micro, _, _ = sys.version_info
        if major == 2:
            names, varargs, keywords, defaults = inspect.getargspec(obj_class.__init__) #ArgSpec(args=['self', 'a', 'b', 'c'], varargs=None, keywords=None, defaults=(10, ''))
        else:
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
