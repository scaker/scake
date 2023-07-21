import ray
import copy
import importlib
import inspect
from omegaconf import OmegaConf
from omegaconf.dictconfig import DictConfig
from omegaconf.listconfig import ListConfig
from .libcore import utils
from .libcore.config_loader import ConfigLoader
from .libcore.sck_graph import SckGraph, GRAPH_EDGE, GRAPH_NODE
from .libcore import sck_format

import pprint

import sys, os

import logging
_logger = logging.getLogger(__name__)

SCAKE_MODE_CACHE = "buffer"
SCAKE_MODE_LIVE = "live"

class Scake(object):
    def __init__(self, module_dir=[], config={}, is_ray=False, is_live=False):
        self.module_dir = module_dir
        self.config = config
        self.is_ray = is_ray
        self.is_live = is_live

        self._conf = ConfigLoader(conf=self.config)
        self.graph = SckGraph(scake=self, config=self._conf.get_config())
        self._cache_flatten = OmegaConf.to_container(ConfigLoader(conf=self.config, 
            is_set_const_flatten_value=False, 
            const_flatten_value=None, 
            is_use_flatten=True
        ).get_config(), resolve=False)

        if isinstance(module_dir, (tuple, list)):
            self.load_modules(self.module_dir)
        else:
            self.load_module(self.module_dir)
        self.load_modules(self._conf.get("_import", []))

        # initialize ray pool
        if self.is_ray:
            num_cpus = self.get("scake.num_cpus", 4)
            ray.init(num_cpus=num_cpus)
            _logger.info("Initialized RAY server with %d cores!" % num_cpus)
        pass

    def load_modules(self, module_dirs):
        if not module_dirs:
            return
        for md in module_dirs:
            self.load_module(md)

    def load_module(self, module_dir):
        if not module_dir:
            return
        if os.path.isdir(module_dir): # abs path
            sys.path.append(module_dir)
            print("Loaded path:", module_dir)
        else:
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), module_dir)))

    def get(self, key, default=None, live=None):
        """
            "scake.num_cpus", 10 => 4
            "scake[num_cpus]", 10 => 4
        """
        live = self.is_live if live is None else live
        return self.graph.query(key=key, default=default, live=live)

    def __getitem__(self, key):
        return self.get(key, default=None, live=None)

    # def set(self, key, value, force_add=True):
    #     self._conf.set(key, value, force_add=force_add)

    # def __setitem__(self, key, value):
    #     self.set(key, value)

    def __call__(self, node_names=[]):
        return self.graph.query(keys=node_names, live=True)

        # --------------------------------------

        if is_rebuild_graph:
            self.graph.build_graph()

        if isinstance(scake_refs, str):
            scake_refs = [scake_refs,]

        print("---------------------------------------------------")
        # print(self.graph.list_graph_str())
        node_exe_layers = self.graph.compute_exec_flow() # [['=/config/bar/a', '=/config/bar/d', '=/config/bar/e'], ['=/config/bar/c', '=/config/bar/f', '=/foo/bar/mysum1()/sum/new_a', '=/foo/bar/mysum1()/sum/new_b', '=/foo/bar/mysum3()/sum/new_a', '=/foo/bar/mysum3()/sum/new_b'], ['=/config/bar'], ['=/config', '=/foo/bar/$foo.bar.Bar'], ['=/foo/bar'], ['=/entry/main2()/foo.bar.__call__', '=/foo', '=/foo/bar/mysum1()/sum', '=/foo/bar/mysum3()/sum'], ['=/entry/main2()', '=/foo/bar/mysum1()', '=/foo/bar/mysum3()'], ['=/entry/main3'], ['=/entry']]

        if not scake_refs:
            self.exec_flow(node_layers=node_exe_layers)
        else:
            # modify node_exe_layers
            modified_exe_layers = []
            keep_nodes = copy.deepcopy(scake_refs)
            for sck_ref in scake_refs:
                for node_from, node_to in self.graph.graph[GRAPH_EDGE]:
                    if node_from == sck_ref:
                        keep_nodes.append(node_to)
            for layer in node_exe_layers:
                new_layer = [node for node in layer if node in keep_nodes]
                if len(new_layer)>0:
                    modified_exe_layers.append(new_layer)

            # print("node_exe_layers", node_exe_layers)
            print("modified_exe_layers", modified_exe_layers)
            # raise Exception("modified_exe_layers")

            self.exec_flow(node_layers=modified_exe_layers)
            pass
        raise Exception("done build")
        return self

    def exec_node(self, node_name, conf=OmegaConf.create(), cache={}, prefer_cache=True):
        """
            Resolve node, write the result to cache and return the result
        """

        if isinstance(node_name, DictConfig):
            return { 
                key: self.exec_node(node_name=value, conf=conf, cache=cache) for (key, value) in node_name.items()
            }
        elif isinstance(node_name, ListConfig):
            return [
                self.exec_node(item, conf=conf, cache=cache) for item in node_name
            ]
        else:
            if isinstance(node_name, str) and sck_format.is_scake_ref(node_name):
                node_value_in_conf = conf.get(sck_format.convert_sckref_to_query(node_name), None)
                node_value_in_cache = cache.get(node_name, None)

                # if prefer_cache and node_value_in_cache is not None:
                #     return node_value_in_cache

                result = None
                if sck_format.is_scake_class(node_name):
                    # $Bar: {"param1": "v1", "param2": "v2", ...}
                    # $Bar: /abc/def
                    if isinstance(node_value_in_conf, DictConfig) or sck_format.is_scake_ref(node_value_in_conf):  
                        result = self.exec_node(node_name=node_value_in_conf, conf=conf, cache=cache)
                        cache[node_name] = result
                        print("Cache set:", node_name, "=>", result)
                    else:
                        raise Exception("Not handling yet! %s, %s" % (node_name, str(node_value_in_conf)))
                    pass
                elif sck_format.is_scake_method(node_name):
                    """
                        mysum2(): __call__
                        # main(): foo.bar.__call__
                        mysum3(): {"sum": {"p1": ..., "p2": ...}}
                        # mysum4(): {"foo.bar.__call__": {"p1": ..., "p2": ...}}
                    """
                    # trigger function
                    target_obj = self.exec_node(node_name=sck_format.get_parent_node(node_name), conf=conf, cache=cache)
                    func_value = self.exec_node(node_name=node_value_in_conf, conf=conf, cache=cache)
                    result = self.__trigger(target_obj, func_value)
                    cache[node_name] = result
                    pass
                elif sck_format.is_scake_ref(node_value_in_conf):
                    # result = cache.get(node_value_in_conf, None)
                    result = self.exec_node(node_name=node_value_in_conf, conf=conf, cache=cache)
                    cache[node_name] = result
                    print("Cache set:", node_name, "=>", result)
                elif type(node_value_in_conf) in (int, float, str, bool):   # primitive type
                    result = node_value_in_conf
                    cache[node_name] = result
                    print("Cache set:", node_name, "=>", result)
                elif isinstance(node_value_in_conf, DictConfig):
                    # if node_name == "/foo/bar":
                    #     print("node_value_in_conf", node_value_in_conf)
                    #     raise Exception()
                    if sck_format.contains_scake_class(node_value_in_conf):
                        # initialize instance
                        # print("Instantiate class", ..., ...)
                        class_str, param_dict = sck_format.extract_class_str_and_param_dict(node_value_in_conf)
                        param_dict = self.exec_node(node_name=param_dict, conf=conf, cache=cache)
                        result = self.__init_instance(class_str=class_str, param_dict=param_dict)
                    else:
                        result = self.exec_node(node_name=node_value_in_conf, conf=conf, cache=cache)
                    cache[node_name] = result
                    print("Cache set:", node_name, "=>", result)
                elif isinstance(node_value_in_conf, ListConfig):
                    result = self.exec_node(node_name=node_value_in_conf, conf=conf, cache=cache)
                    cache[node_name] = result
                    print("Cache set:", node_name, "=>", result)
                else:
                    raise Exception("Not handling case! node_name (%s), node_value_in_conf(%s), node_value_in_cache(%s)" % (node_name, str(node_value_in_conf), str(node_value_in_cache)))
                    return node_name #?!
                    pass
                return result
                pass
            else:
                return node_name
            pass
        

    def exec_flow(self, node_layers):
        """
            Execute layer by layer
        """

        print("self._cache_flatten", self._cache_flatten)

        ncount = 0
        for nlayer in node_layers: # ['/config/bar/a', '/config/bar/e']
            for node_name in nlayer:
                result = self.exec_node(node_name, conf=self._conf, cache=self._cache_flatten)
                # print("****************", node_name, "=>", result)
                # if node_name == "/foo/bar/$foo.bar.Bar":
                #     raise Exception()
                ncount += 1
                # if ncount >= 10000000:
                #     print(str(self._cache_flatten).replace("None", "'None'").replace("True", "'True'").replace("'", '"'))
                #     raise Exception("stop")
            pass
        
        # # update cache
        # self._cache_flatten = self._conf.merge(base=self._cache_flatten.get_config(), new=OmegaConf.create(my_cache))

        print(str(self._cache_flatten).replace("None", "'None'").replace("True", "'True'").replace("'", '"'))
        raise Exception("stop2")
        pass
        