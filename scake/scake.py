import ray
import copy
from omegaconf import OmegaConf
from .libcore import utils
from .libcore.config_loader import ConfigLoader
from .libcore.sck_graph import SckGraph, GRAPH_EDGE, GRAPH_NODE
from .libcore import sck_format

import sys, os

import logging
_logger = logging.getLogger(__name__)

SCAKE_MODE_CACHE = "buffer"
SCAKE_MODE_LIVE = "live"

class Scake(object):
    def __init__(self, module_dir=[], config={}, is_ray=False, mode=SCAKE_MODE_CACHE):
        self.module_dir = module_dir
        self.config = config
        self.is_ray = is_ray
        self._conf_manager = ConfigLoader(conf=self.config)
        self.graph = SckGraph(scake=self, config=self._conf_manager.get_config())
        self.mode = mode
        self._cache = ConfigLoader()

        if isinstance(module_dir, (tuple, list)):
            self.load_modules(self.module_dir)
        else:
            self.load_module(self.module_dir)
        self.load_modules(self._conf_manager.get("_import", []))

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

    # def get(self, key, default=None, cache=False, live=False):
    #     """
    #         "scake.num_cpus", 10 => 4
    #         "scake[num_cpus]", 10 => 4
    #     """
    #     mode = self.mode
    #     if cache and live: # both are True => use self.mode
    #         pass
    #     elif cache:
    #         mode = SCAKE_MODE_CACHE
    #     elif live:
    #         mode = SCAKE_MODE_LIVE
    #     else:
    #         pass

    #     if mode == SCAKE_MODE_CACHE:
    #         result = self._cache.get(key, default=None) and self._conf_manager.get(key, default=default)
    #     else:
    #         result = self.__call__(scake_refs=[sck_format. (key),])
    #     return result

    # def __getitem__(self, key):
    #     return self.get(key, None)

    # def set(self, key, value, force_add=True):
    #     self._conf_manager.set(key, value, force_add=force_add)

    # def __setitem__(self, key, value):
    #     self.set(key, value)

    def __call__(self, scake_refs=[], is_rebuild_graph=False):
        if is_rebuild_graph:
            self.graph.build_graph()

        if isinstance(scake_refs, str):
            scake_refs = [scake_refs,]

        print("---------------------------------------------------")
        print(self.graph.list_graph_str())
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

            print("modified_exe_layers", modified_exe_layers)
            raise Exception("modified_exe_layers")

            self.exec_flow(node_layers=modified_exe_layers)
            pass
        raise Exception("done build")
        return self

    def exec_flow(self, node_layers):
        
        pass
