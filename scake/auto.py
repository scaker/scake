# -*- coding: utf-8 -*-
import os
import sys
import inspect
import yaml
from .scake import Scake
from .structure import ScakeDict


class AutoScake():
    def __init__(self, exec_graph, node_path=['scake'], root=None):
        if isinstance(exec_graph, dict) or isinstance(exec_graph, ScakeDict):
            # no pre-processing
            pass
        elif os.path.isfile(exec_graph) and (exec_graph.endswith('.yaml') or exec_graph.endswith('.yml')):
            with open(exec_graph) as f:
                data_dict = yaml.safe_load(f)
            exec_graph = data_dict

        assert isinstance(exec_graph, dict) or isinstance(
            exec_graph, ScakeDict)
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

    def run(self):
        last_length_wait_dict = len(self.wait_dict)
        # num_retry = 0
        # print('Wait Dict while running...')
        while True:
            # print('run() > wait_dict', self.wait_dict)
            # print('---')
            self.__run_recursive(self.__dict__)
            if len(self.wait_dict) == 0:
                break

            self.__check_wait_dict_and_reinit()

            if len(self.wait_dict) == last_length_wait_dict:
                print('Break due to length of wait_dict has not been changed: len(self.wait_dict) =',
                      len(self.wait_dict))
                break
            last_length_wait_dict = len(self.wait_dict)
        pass

    def __run_recursive(self, root):
        for key, value in root.items():
            # skip special keys
            if key in ['obj', 'root', 'exec_graph'] or isinstance(value, AutoScake):
                continue
            if isinstance(value, dict):
                self.__run_recursive(value)
            elif '__call__' in dir(value) and not hasattr(value, '_scake_run'):
                result = value()
                for wfield in getattr(value, '_scake_waiting_fields'):
                    setattr(value, wfield, result)
                setattr(value, '_scake_run', 1)
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
                updated_node_path = self.node_path[:]  # copy list
                updated_node_path.append(key)
                comp = self.__get_scake_component(
                    component_str='.'.join(updated_node_path), root=self.root)
                if comp and comp.is_done_init and (not isinstance(comp, dict)) and (not isinstance(comp, ScakeDict)):
                    parsed_dict[key] = comp
                else:
                    auto = AutoScake(exec_graph=value,
                                     node_path=updated_node_path,
                                     root=self.root)
                    if not auto.is_done_init:
                        self.is_done_init = False
                    setattr(self, key, auto.obj)
                    parsed_dict[key] = auto.obj
            else:
                if isinstance(value, str) and value.startswith('scake'):
                    if value.count('.') == 0:
                        raise Exception(
                            'Invalid reference to scake component: %s' % value)
                    component = self.__get_scake_component(
                        component_str=value, root=self.root)
                    not_call_annotation = (not isinstance(component, str)) or (component not in [
                        '()', '__call__', '__call__()'])
                    if component and not_call_annotation:
                        setattr(self, key, component)
                        parsed_dict[key] = component
                        self.root.wait_dict.pop(value, None)
                    else:
                        # print('Component not found @', value)
                        self.is_done_init = False
                        self.root.wait_dict[value] = '.'.join(self.node_path)
                        # print('self.root.wait_dict', self.root.wait_dict)
                        pass
                    pass
                else:
                    setattr(self, key, value)
                    parsed_dict[key] = value
            pass

        for key, value in exec_graph.items():
            if key in Scake.CLASSES_DICT.keys():
                auto = getattr(self, key)
                if auto.is_done_init:
                    # print('key', key, 'param', auto)
                    new_instance = self.__init_instance(
                        class_str=key, param_dict=auto)  # override self.obj
                    waiting_fields = []
                    # copy all parsed_dict to the new instance
                    for pkey, pvalue in parsed_dict.items():
                        # this variable will handle the result of __call__() method
                        if pvalue is None or pvalue in ['()', '__call__', '__call__()']:
                            waiting_fields.append(pkey)
                        else:
                            setattr(new_instance, pkey, pvalue)
                    setattr(new_instance, '_scake_waiting_fields',
                            waiting_fields)
                    parsed_dict = new_instance
                    # print('* new instance:', self.node_path)
                    # pprint(vars(new_instance))
                else:
                    # print('** Component not found @', value)
                    self.is_done_init = False
                    # self.root.wait_dict[value] = '.'.join(node_path)
                    # print('self.root.wait_dict', self.root.wait_dict)
                    pass
                break
            pass
        return parsed_dict

    def __init_instance(self, class_str, param_dict):
        # loop up in "CLASSES_DICT"
        obj_class = Scake.CLASSES_DICT[class_str]
        init_params = param_dict

        major, minor, micro, _, _ = sys.version_info
        if major == 2:
            # ArgSpec(args=['self', 'a', 'b', 'c'], varargs=None, keywords=None, defaults=(10, ''))
            names, varargs, keywords, defaults = inspect.getargspec(
                obj_class.__init__)
        else:
            names, varargs, keywords, defaults, kwonlyargs, kwonlydefaults, annotations = inspect.getfullargspec(
                obj_class.__init__)  # https://docs.python.org/3.4/library/inspect.html#inspect.getfullargspec
        names = names[1:]
        defaults = [] if not defaults else defaults
        if len(names) > len(defaults):
            # check required params
            num_required_names = len(names) - len(defaults)
            required_names = names[:num_required_names]
            for rn in required_names:
                if rn not in init_params:
                    raise Exception(
                        'Missing required param "%s" of %s' % (rn, class_str))

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

    # def get():
    #    return self.obj
