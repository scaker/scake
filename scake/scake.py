# -*- coding: utf-8 -*-
import sys
import inspect
# import importlib

from .graph import NodeGraph
from .rule import Rule


class Scake():
    def __init__(self, config, rule=None, class_mapping=None):
        self._config = config
        self._config_dict = config
        self._class_mapping = class_mapping
        self._rule = rule or Rule()
        self._flat_dict = self._build_config(self._config_dict)
        self._node_graph = self._build_nodes(self._flat_dict)
        self._runtime_nodes_order = []
        pass

    def _get_recursive_value(self, value):
        ref_key = self._rule.is_ref(value)
        if ref_key:
            return self[ref_key]
        elif isinstance(value, dict):
            new_item = {}
            for k, v in value.items():
                new_item[k] = self._get_recursive_value(value=v)
            return new_item
        elif isinstance(value, list):
            new_item = []
            for v in value:
                new_item.append(self._get_recursive_value(value=v))
            return new_item
        else:
            return value
        pass

    def __getitem__(self, key):
        k = self._flat_dict[key]
        v = self._get_recursive_value(value=k)
        return v

    def __setitem__(self, key, value):
        self._flat_dict[key] = value

    def __len__(self):
        return len(self._flat_dict)

    def __repr__(self):
        content = []
        sorted_k = sorted(list(self._flat_dict))
        for k in sorted_k:
            content.append('%s: %s' % (k, str(self._flat_dict[k])))
        return """
            Scake Object:
                * _config: %(_config)s
                * _flat_dict:
%(_content)s
        """ % {
            '_config': self._config,
            '_content': '\n'.join(content)
        }

    def exec_nodes(self):
        #         print('len(self._runtime_nodes_order)', len(self._runtime_nodes_order))
        node_zero_degree = [n for n in self._runtime_nodes_order if n.degree == 0]
#         print('len(self.node_zero_degree)', len(node_zero_degree))
        for node in node_zero_degree:
            if self._rule.is_method(node.id):
                # execute method
                obj = self[self._parent(key=node.id)]

                func_value = self[node.id]
                if isinstance(func_value, dict):
                    func_name = list(func_value.keys())[0]
                    func_params = list(func_value.values())[0]
                    func = getattr(obj, func_name)
                    self[node.id] = func(**func_params)
                elif isinstance(func_value, str):  # call method with no params
                    func_name = func_value
                    func = getattr(obj, func_name)
                    self[node.id] = func()

                node.resolve()
            else:
                def child_nodes_filter(k): return k.startswith(node.id) and k != node.id and k.count(
                    self._rule.separator)-node.id.count(self._rule.separator) == 1
                sub_ids = self._filter_keys(condition=child_nodes_filter)
                classname_list = [self._rule.is_class(id) for id in sub_ids]
                num_classnames = sum([c is not None for c in classname_list])
                if num_classnames == 1:
                    cidx = 0
                    for c in classname_list:
                        if c is not None:
                            break
                        cidx += 1

                    param_id = sub_ids[cidx]
                    classname = classname_list[cidx]

                    self[node.id] = self.__init_instance(self._class_mapping, classname, self[param_id])
                    node.resolve()
                    pass
                elif num_classnames > 1:
                    raise Exception('There are more than one class constructor: %s' % str(sub_ids))
                else:
                    node.resolve()
                    pass
            pass
        pass

    def run(self):
        self._runtime_nodes_order = self._node_graph.get_node_order()
        while len(self._runtime_nodes_order) > 0:
            self.exec_nodes()
#             break
            self._runtime_nodes_order = self._node_graph.get_node_order()
        pass

    def _filter_keys(self, condition):
        keys = []
        for k in sorted(list(self._flat_dict.keys())):
            if condition(k):
                keys.append(k)
            pass
        return keys

    def _extract_dependencies(self, key_list):
        deps = []
        for k in key_list:
            v = self._flat_dict[k]
            ref_key = self._rule.is_ref(v)
            deps.append(ref_key) if ref_key else None
            pass
        return deps

    def _parent(self, key):
        key_parts = key.split(self._rule.separator)
        return self._rule.separator.join(key_parts[:-1])

    def _build_nodes(self, flat_dict):
        node_graph = NodeGraph(self)
        node_ids = self._filter_keys(condition=lambda k: self._rule.is_class(k) or self._rule.is_method(k))
        for id in node_ids:
            des_ids = self._filter_keys(condition=lambda k: k.startswith(id))
            deps = self._extract_dependencies(des_ids)
            node_graph.add_node(id=id, des_paths=deps)

            # special cases: class, method
            if self._rule.is_class(id):
                node_graph.add_node(id=self._parent(id), des_paths=[id])
            elif self._rule.is_method(id):
                node_graph.add_node(id=id, des_paths=[self._parent(id)])

        return node_graph

    def _merge_dicts(self, keep, target, prefix):
        for key, value in target.items():
            keep[self._rule.separator + prefix + key] = value
        return keep

    def _build_config(self, config):
        flat_dict = {}
        if isinstance(config, dict):
            for k, v in config.items():
                sub_flat_dict = self._build_config(v)
                if sub_flat_dict:
                    flat_dict = self._merge_dicts(keep=flat_dict, target=sub_flat_dict, prefix=k)
                flat_dict[self._rule.separator + k] = v
        elif isinstance(config, list) or isinstance(config, tuple):
            for idx, v in enumerate(config):
                sub_flat_dict = self._build_config(v)
                if sub_flat_dict:
                    flat_dict = self._merge_dicts(keep=flat_dict, target=sub_flat_dict, prefix=str(idx))
                flat_dict[self._rule.separator + str(idx)] = v
            pass
        else:
            return None
        return flat_dict

    def __init_instance(self, class_mapping, class_str, param_dict):
        # -- initialize class object --
        # loop up in "class_mapping"
        if class_str not in class_mapping and class_str.count('.') > 0:
            base_package = class_str.split('.')[0]

            if base_package not in class_mapping:
                globals()[base_package] = __import__(base_package)
                self._class_mapping.update(globals())
            class_pointer = eval(class_str)
            self._class_mapping[class_str] = class_pointer
            class_mapping = self._class_mapping

        obj_class = class_mapping[class_str]
        # -----------------------------

        init_params = param_dict

        if isinstance(init_params, dict):
            # -- initialize for dictionary of parameters --
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
            pass
        elif isinstance(init_params, list):
            obj = obj_class(*init_params)
        else:
            raise Exception('Class parameters type is not supported!')

        return obj
