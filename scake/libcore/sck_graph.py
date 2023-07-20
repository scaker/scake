# -*- coding: utf-8 -*-
import re
import operator
import copy
from omegaconf import OmegaConf
from omegaconf.dictconfig import DictConfig
from omegaconf.listconfig import ListConfig
from omegaconf.errors import InterpolationKeyError
from .config_loader import ConfigLoader
from . import sck_format

GRAPH_EDGE = "edge"
GRAPH_NODE = "node"

class SckGraph():
    def __init__(self, scake, config=None):
        self.scake = scake
        self.graph = {
            GRAPH_EDGE: {},
            GRAPH_NODE: {},
            # "edge": {
            #     (<node_from>, <node_to),
            #     ("config.bar.c", "config.bar.a"),
            # }
        }
        self.config = OmegaConf.create() if not config else config
        self.build_graph()
        pass

    def set_config(self, config):
        self.config = config

    def _get_node_name_from_method_description(self, description):
        """
            description:
                - "sum"
                - "foo.bar.__call__"
                - {"sum": {"new_a": 1, "new_b": 2}}                
                - {"foo.bar.__call__": {"new_a": 1, "new_b": 2}}
        """
        if isinstance(description, str):
            if description.count(".") > 0:  # foo.bar.__call__
                return sck_format.convert_list_to_sckref(description.split(".")[:-1])    # =/foo/bar
            else:   # sum, __call__ (local method)
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
            #TODO
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
        # result.append("* Edge (%d)" % len(self.graph[GRAPH_EDGE]))
        # for idx, sedge in enumerate(sorted_edges):
        #     result.append("%d. %s -> %s" % (idx+1, sedge[0], sedge[1]))
        
        # result.append("* Nodes (%d)" % len(self.graph[GRAPH_NODE]))
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
                # del graph_result[GRAPH_NODE][node]["in"][node_name]
                # del graph_result[GRAPH_NODE][node]["out"][node_name]
                graph_result[GRAPH_NODE][node]["in"].pop(node_name, None)
                graph_result[GRAPH_NODE][node]["out"].pop(node_name, None)
                pass
        # del graph_result[GRAPH_NODE].pop[node_name]
        graph_result[GRAPH_NODE].pop(node_name, None)
        return graph_result

    def compute_exec_flow(self, graph=None):
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
        
        current_layer = []
        for node_info in result:
            n_out, n_in, node_name, _ = node_info
            if n_out == 0:
                current_layer.append(node_name)
                pass

        for node_name in current_layer:
            graph = self.delete_node_from_graph(graph, node_name)

        return [current_layer] + self.compute_exec_flow(graph)

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

            print("add_edge:", node_from, "->", node_to)
            # print("self.graph", self.graph)

    def build_graph(self, config=None, parent_path=[]):
        """
            - Param config is a "OmegaConf" object
            - Build node dependencies
        """
        if config is None:
            config = self.config
            
        print("-Build_graph:", config, parent_path)
        
        for k, v in config.items():
            print("Traverse:", k, v, type(v))
            if k in ConfigLoader.RESERVED_KEYS:
                continue
                
            # if k.startswith("$"):   # class
            #     print("init class", k, v)
            #     pass
            # elif k.count("(")==1 and k.count(")")==1:   # method, main(), mysum3(sum), main2(${foo.bar.__call__})
            #     #TODO
            #     print("method found", k, v)
            #     pass

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
                        if not target_obj_node_name:
                            target_obj_node_name = sck_format.convert_list_to_sckref(parent_path)
                        
                        method_name = list(set(list(v.keys())) - set(["_multi",]))[0]
                        self.add_edge(
                            sck_format.convert_list_to_sckref(parent_path+[k, method_name]),
                            target_obj_node_name
                        )
                        is_add_connection = False

                        # print("is sckae method", k, target_obj_node_name)
                        # raise Exception()
                        pass

                pass
            else:   # v is primitive type
                # do not add connection
                is_add_connection = False

                # # main(): foo.bar.__call__
                # if sck_format.is_scake_method(k):
                #     if v.count(".")
                pass
            pass

            if is_add_connection and parent_path:
                # create relationship from parent to child (current node)
                self.add_edge(sck_format.convert_list_to_sckref(parent_path), sck_format.convert_list_to_sckref(parent_path+[k,]))
        pass
        