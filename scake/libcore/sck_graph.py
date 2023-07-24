# -*- coding: utf-8 -*-
import sys, inspect
import re
import operator
import copy
import importlib
from omegaconf import OmegaConf
from omegaconf.dictconfig import DictConfig
from omegaconf.listconfig import ListConfig
from omegaconf.errors import InterpolationKeyError
from .config_loader import ConfigLoader
from . import sck_format
from .sck_log import sck_log

import logging
_logger = logging.getLogger(__name__)

GRAPH_EDGE = "edge"
GRAPH_NODE = "node"
GRAPH_NODE_RESOLVED_VALUE = "resolved_value"

class SckGraph():
    def __init__(self, scake, config=None):
        self.scake = scake
        self.graph = self._get_empty_graph()
        self.set_config(config)
        pass

    def _get_empty_graph(self):
        return {
            GRAPH_EDGE: {},
            GRAPH_NODE: {},
            # "edge": {
            #     (<node_from>, <node_to),
            #     ("config.bar.c", "config.bar.a"),
            # }
        }

    def set_config(self, config={}):
        self.config = config
        self.build_graph()

    def _get_node_name_from_method_description(self, description):
        """
            description:
                - "sum"
                - "foo.bar.__call__"
                - {"sum": {"new_a": 1, "new_b": 2}}                
                - {"foo.bar.__call__": {"new_a": 1, "new_b": 2}}
        """
        if isinstance(description, str):
            return None
        elif isinstance(description, DictConfig):
            method_name = False
            for k, v in description.items():
                if k in ("_multi",):
                    continue
                method_name = k
                break
            return self._get_node_name_from_method_description(method_name)
        elif isinstance(description, ListConfig):
            raise Exception("TODO")
            pass
        return None
        pass
        
    def _is_node_exist(self, node_name):
        return node_name in self.graph[GRAPH_NODE]

    def _is_edge_exist(self, node_from, node_to):
        return (node_from, node_to) in self.graph[GRAPH_EDGE]

    def list_graph_str(self):
        edges = list(self.graph[GRAPH_EDGE].keys())
        sorted_edges = sorted(edges, key=lambda tup: tup[0])

        result = []
        for idx, node_name in enumerate(sorted(self.graph[GRAPH_NODE].keys())):
            node_info = self.graph[GRAPH_NODE][node_name]
            result.append((
                len(node_info["out"]), 
                len(node_info["in"]), 
                node_name, 
                "%s: in(%d)=%s, out(%d)=%s" % (node_name, len(node_info["in"]), str(list(node_info["in"].keys())), len(node_info["out"]), str(list(node_info["out"].keys())))
            ))
        
        # # https://stackoverflow.com/a/29849371
        # ORDER BY name ASC, age DESC
        # items.sort(key=operator.itemgetter('age'), reverse=True)
        # items.sort(key=operator.itemgetter('name'))
        result.sort(key=lambda tup: tup[2])     # name
        # result.sort(key=lambda tup: tup[1])     # in
        result.sort(key=lambda tup: tup[0])     # out
        result = [("%d. " % (idx+1))  + item[3] for idx, item in enumerate(result)]

        result.insert(0, "* Nodes (%d)" % len(self.graph[GRAPH_NODE]))
        result.insert(0, "----------------------")
        result.insert(len(result), "----------------------")

        return "\n".join(result)

    def delete_node_from_graph(self, graph, node_name):
        graph_result = copy.deepcopy(graph)

        for edge in list(graph[GRAPH_EDGE].keys()):
            if node_name in edge:
                # del graph_result[GRAPH_EDGE][edge]
                graph_result[GRAPH_EDGE].pop(edge, None)

        for node, ndata in list(graph[GRAPH_NODE].items()):
            if node == node_name:
                continue
            else:
                graph_result[GRAPH_NODE][node]["in"].pop(node_name, None)
                graph_result[GRAPH_NODE][node]["out"].pop(node_name, None)
                pass
        # del graph_result[GRAPH_NODE].pop[node_name]
        graph_result[GRAPH_NODE].pop(node_name, None)
        return graph_result

    def compute_exec_flow(self, node_names=[], graph=None):        
        if not graph:
            graph = copy.deepcopy(self.graph)
        else:
            if len(graph[GRAPH_NODE]) == 0:
                return []
            graph = copy.deepcopy(graph)

        result = []
        for idx, node_name in enumerate(sorted(graph[GRAPH_NODE].keys())):
            node_info = graph[GRAPH_NODE][node_name]
            result.append((
                len(node_info["out"]), 
                len(node_info["in"]), 
                node_name, 
                "%s: in(%d)=%s, out(%d)=%s" % (node_name, len(node_info["in"]), str(list(node_info["in"].keys())), len(node_info["out"]), str(list(node_info["out"].keys())))
            ))

        result.sort(key=lambda tup: tup[0])     # out
        
        selected_nodes = copy.deepcopy(node_names)
        for nname in node_names:
            selected_nodes += [node_to for node_from, node_to in graph[GRAPH_EDGE].keys() if node_from == nname]

        current_layer = []
        for node_info in result:
            n_out, n_in, node_name, _ = node_info
            if n_out == 0:
                if not selected_nodes or (selected_nodes and node_name in selected_nodes):
                    current_layer.append(node_name)
                pass

        if not current_layer:
            return []   # avoid infinitive recursive call

        for node_name in current_layer:
            graph = self.delete_node_from_graph(graph, node_name)

        return [current_layer] + self.compute_exec_flow(node_names=node_names, graph=graph)

    def add_node(self, node_name):
        self.graph[GRAPH_NODE].setdefault(node_name, {"in": {}, "out": {}})

    def update_parent_dependencies(self, parent_nodes, target_node):
        """
            parent_nodes = {"node1": True, "node2": True, ...}
            target_node = "nodex"
        """
        for pnode in parent_nodes.keys():
            self.add_edge(node_from=pnode, node_to=target_node)

    def update_child_dependencies(self, source_node, child_nodes):
        for cnode in child_nodes.keys():
            self.add_edge(node_from=source_node, node_to=cnode)

    def add_edge(self, node_from, node_to, is_add_node=True):
        if is_add_node:
            for node_name in (node_from, node_to):
                self.add_node(node_name)

        if self._is_edge_exist(node_from, node_to):
            # skip it
            pass
        else:
            self.graph[GRAPH_EDGE].setdefault((node_from, node_to), True)
            self.graph[GRAPH_NODE][node_from]["out"][node_to] = True
            self.graph[GRAPH_NODE][node_to]["in"][node_from] = True
            self.update_parent_dependencies(parent_nodes=self.graph[GRAPH_NODE][node_from]["in"], target_node=node_to)
            self.update_child_dependencies(source_node=node_from, child_nodes=self.graph[GRAPH_NODE][node_to]["out"])
            
    def build_graph(self, config=None, parent_path=[]):
        """
            - Param config is a "OmegaConf" object
            - Build node dependencies
        """
        if config is None:
            config = self.config
        
        if not sck_format.is_dict(config):
            return

        for k, v in config.items():
            if k in ConfigLoader.RESERVED_KEYS:
                continue
                
            is_add_connection = True
            if sck_format.is_scake_ref(v):
                node_from = sck_format.convert_list_to_sckref(parent_path+[k,])
                node_to = v
                self.add_edge(node_from, node_to)                
            elif isinstance(v, (DictConfig, ListConfig)):
                if isinstance(v, ListConfig):
                    for idx, item in enumerate(v):
                        self.add_edge(sck_format.convert_list_to_sckref(parent_path+[k,]), sck_format.convert_list_to_sckref(parent_path+[k, str(idx)]))
                        self.build_graph(item, parent_path=parent_path+[k, str(idx)])   # a/b/c/3
                elif isinstance(v, DictConfig):
                    self.build_graph(v, parent_path=parent_path+[k,])

                    # mysum1(): {<method_name>: {<param_1>: <val_1>, <param_2>: <val_2>}}
                    if sck_format.is_scake_method(k):
                        target_obj_node_name = self._get_node_name_from_method_description(v)
                        if not target_obj_node_name:    # is None
                            target_obj_node_name = sck_format.convert_list_to_sckref(parent_path)
                        
                        method_name = list(set(list(v.keys())) - set(["_multi",]))[0]
                        self.add_edge(
                            sck_format.convert_list_to_sckref(parent_path+[k, method_name]),
                            target_obj_node_name
                        )
                        is_add_connection = False
                        pass
                pass
            else:   # v is primitive type            
                if sck_format.is_scake_method(k):
                    # link method to its parent
                    self.add_edge(
                        sck_format.convert_list_to_sckref(parent_path+[k,]),
                        sck_format.convert_list_to_sckref(parent_path)
                    )
                    # do not add connection
                    is_add_connection = False
                pass
            pass

            if is_add_connection and parent_path:
                # create relationship from parent to child (current node)
                self.add_edge(sck_format.convert_list_to_sckref(parent_path), sck_format.convert_list_to_sckref(parent_path+[k,]))
        pass
    
    def query(self, key=None, keys=[], default=None, live=False):
        if key:
            keys = copy.deepcopy(keys)
            keys += [key,]
        
        # standardize and validate query keys
        new_keys = []
        for qkey in keys:
            nkey = qkey
            if not sck_format.is_scake_ref(qkey) and not qkey.startswith(sck_format.SCK_ANNO_REF_START):
                nkey = sck_format.SCK_ANNO_REF_START+qkey
            if not sck_format.is_scake_ref(nkey):
                raise Exception("Invalid format for query: %s. Correct query format: /a/b/c/d" % nkey)
            new_keys.append(nkey)
        keys = new_keys        

        exec_layers = self.compute_exec_flow(node_names=keys)   # [["/config/bar/a", ...], ...]

        logw("Exec layers for", keys, ".....", exec_layers)

        for layer in exec_layers:
            for node_name in layer:
                node_resolved_value = self.resolve(key=node_name, default=default, live=live)
                logi("Resolved", node_name, "=>", node_resolved_value)

        # extract result from graph_node
        graph_node = self.graph[GRAPH_NODE]
        if not keys:
            query_result = {node_name: node_info[GRAPH_NODE_RESOLVED_VALUE] for node_name, node_info in graph_node.items()}
        else:
            query_result = {node_name: node_info[GRAPH_NODE_RESOLVED_VALUE] for node_name, node_info in graph_node.items() if node_name in keys}
        
        if keys:
            if len(keys) == 1:
                query_result = query_result[keys[0]]
            else:
                query_result = [query_result[xk] for xk in keys]
            pass

        return query_result

    def resolve(self, key, default=None, live=False):
        """
            key="/config/bar/a", node_value=1
        """
        # node_name = key
        graph_node = self.graph[GRAPH_NODE]

        target = key
        final_result = None
        p_queue = [{"node": target, "result_description": {}},]
        while len(p_queue)>0:
            logw("|=======p queue=======|", p_queue)
            n_item = len(p_queue)
            for idx in range(n_item):
                p_item = p_queue[idx]
                target = p_item["node"]
                result_description = p_item["result_description"]

                logd("->Check cache", "live mode", live, "target", target, "node info", graph_node.get(target, {}))

                res_value = OmegaConf.select(self.config, sck_format.convert_sckref_to_query(target), default=None)

                # check "resolved_value" of the node if any
                if not live and GRAPH_NODE_RESOLVED_VALUE in graph_node.get(target, {}) or \
                    (sck_format.contains_scake_class(res_value) and GRAPH_NODE_RESOLVED_VALUE in graph_node.get(target, {})): # force using reference from initialized object, because the executive layers are resolved in order
                    res_value = graph_node[target][GRAPH_NODE_RESOLVED_VALUE]
                    if not result_description:
                        final_result = res_value # already the result we want. Eg. 1, 5 "x"
                        break
                    else:
                        self._apply_result_description(result_description, res_value)
                        pass
                    continue

                if sck_format.is_scake_method(target):
                    """
                        mysum2(): __call__
                        # main(): foo.bar.__call__
                        mysum3(): {"sum": {"p1": ..., "p2": ...}}
                        # mysum4(): {"foo.bar.__call__": {"p1": ..., "p2": ...}}
                    """
                    # trigger function
                    parent_node = sck_format.get_parent_node(target)

                    logd("....... key", key, "target", target, "parent_node", parent_node)

                    target_obj =  graph_node[parent_node][GRAPH_NODE_RESOLVED_VALUE]

                    if sck_format.is_dict(res_value):
                        fname = list(res_value.keys())[0]
                        func_value = {}
                        func_value[fname] = graph_node[sck_format.SCK_REF_DELIMITER.join([target, fname])][GRAPH_NODE_RESOLVED_VALUE] # resolve values
                    else:
                        func_value = res_value # may be a dictionary or a string (call method with no param)
                    
                    method_result = self.__trigger(target_obj, func_value)
                    
                    # for function with no param
                    if not result_description:
                        final_result = method_result
                    else:
                        self._apply_result_description(result_description, method_result)
                    pass
                elif sck_format.is_dict(res_value):
                    init_result = {}

                    is_instance_init = False
                    if sck_format.contains_scake_class(res_value):  # instantiate the object
                        class_str, _ = sck_format.extract_class_str_and_param_dict(res_value)
                        param_dict = graph_node[sck_format.SCK_REF_DELIMITER.join([target, class_str])][GRAPH_NODE_RESOLVED_VALUE]
                        init_result = self.__init_instance(class_str=class_str, param_dict=param_dict)
                        is_instance_init = True

                    if not result_description:
                        final_result = init_result
                        res_dict = final_result
                    else:
                        res_dict = init_result
                        self._apply_result_description(result_description, res_dict) # assign empty dict to result

                    if is_instance_init:
                        # do nothing!
                        pass
                    else:
                        for k, v in res_value.items():
                            p_queue.append({
                                "node": sck_format.SCK_REF_DELIMITER.join([target, k]),
                                "result_description": {
                                    "type": "dict",
                                    "dict": res_dict,
                                    "key": k,
                                }
                            })
                    pass
                elif sck_format.is_list(res_value):
                    if not result_description:
                        final_result = []
                        res_list = final_result
                    else:
                        res_list = []
                        self._apply_result_description(result_description, res_list) # assign empty dict to result

                    for idx, item in enumerate(res_value):
                        p_queue.append({
                            "node": sck_format.SCK_REF_DELIMITER.join([target, str(idx)]),
                            "result_description": {
                                "type": "list",
                                "list": res_list,
                            }
                        })
                    pass
                elif sck_format.is_primitive(res_value):
                    if sck_format.is_scake_ref(res_value): # reference
                        p_queue.append({
                            "node": res_value,
                            "result_description": result_description, # keep result description
                        })
                    else:
                        if not result_description:
                            final_result = res_value # already the result we want. Eg. 1, 5 "x"
                            break
                        else:
                            self._apply_result_description(result_description, res_value)
                            pass
                    pass
                else:   # None, key not found?!
                    if not result_description:
                        final_result = default
                        break
                pass
            p_queue = p_queue[n_item:]

        graph_node[key][GRAPH_NODE_RESOLVED_VALUE] = final_result
        return final_result

    def _apply_result_description(self, result_description, value):
        if not result_description:
            return
        if result_description["type"] == "dict":
            ref_dict = result_description["dict"]
            key = result_description["key"]
            ref_dict[key] = value
        elif result_description["type"] == "list":
            ref_list = result_description["list"]
            ref_list.append(value)

    def __init_instance(self, class_str, param_dict):
        module_name, class_name = class_str.lstrip(sck_format.SCK_ANNO_CLASS).rsplit(".", 1)
        obj_class = getattr(importlib.import_module(module_name), class_name)
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
            raise Exception('Class parameters type (%s) is not supported!' % str(type(init_params)))

        logd("Initialized object %s @ %s => %s" % (str(obj_class), str(init_params), str(obj)))

        return obj
    
    def __trigger(self, target_obj, func_value):
        if isinstance(func_value, (dict, DictConfig)):
            func_name = list(func_value.keys())[0]
            func_params = list(func_value.values())[0]
            func = getattr(target_obj, func_name)
            if isinstance(func_params, (dict, DictConfig)):
                return func(**func_params)
            elif isinstance(func_params, (list, ListConfig)):
                return func(*func_params)
        elif isinstance(func_value, str):  # call method with no params
            func_name = func_value
            func = getattr(target_obj, func_name)
            return func()
        return None

logd = sck_log.register(obj_or_class=SckGraph, is_debug=True)
logi = sck_log.register(obj_or_class=SckGraph, is_info=True)
logw = sck_log.register(obj_or_class=SckGraph, is_warning=True)
loge = sck_log.register(obj_or_class=SckGraph, is_error=True)
