# -*- coding: utf-8 -*-
import logging
import os
import sys

import ray
from omegaconf import OmegaConf

from .libcore.config_loader import ConfigLoader
from .libcore.sck_graph import SckGraph

logging.addLevelName(
    logging.INFO, "\x1b[1;34m%s\x1b[0m" % logging.getLevelName(logging.INFO)
)
logging.addLevelName(
    logging.WARNING, "\x1b[1;33m%s\033[1;0m" % logging.getLevelName(logging.WARNING)
)
logging.addLevelName(
    logging.ERROR, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR)
)
# https://stackoverflow.com/a/23874319
logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    # format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s@%(funcName)s: %(message)s",
    format="%(asctime)s.%(msecs)03d %(levelname)s %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
_logger = logging.getLogger(__name__)


class Scake(object):
    def __init__(self, module_dir=[], config={}, is_ray=False, is_live=False):
        self.module_dir = module_dir
        self.config = config
        self.is_ray = is_ray
        self.is_live = is_live

        self._conf = ConfigLoader(conf=self.config)
        self.graph = SckGraph(scake=self, config=self._conf.get_config())
        self._cache_flatten = OmegaConf.to_container(
            ConfigLoader(
                conf=self.config,
                is_set_const_flatten_value=False,
                const_flatten_value=None,
                is_use_flatten=True,
            ).get_config(),
            resolve=False,
        )

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

    def load_modules(self, module_dirs):
        if not module_dirs:
            return
        for md in module_dirs:
            self.load_module(md)

    def load_module(self, module_dir):
        if not module_dir:
            return
        if os.path.isdir(module_dir):  # abs path
            sys.path.append(module_dir)
            print("Loaded path:", module_dir)
        else:
            sys.path.append(
                os.path.abspath(os.path.join(os.path.dirname(__file__), module_dir))
            )

    def get(self, key, default=None, live=None):
        """
        "scake.num_cpus", 10 => 4
        "scake[num_cpus]", 10 => 4
        """
        live = self.is_live if live is None else live
        return self.graph.query(key=key, default=default, live=live)

    def __getitem__(self, key):
        return self.get(key=key, default=None, live=None)

    # def set(self, key, value, force_add=True):
    #     self._conf.set(key, value, force_add=force_add)

    # def __setitem__(self, key, value):
    #     self.set(key, value)

    def __call__(self, node_names=[]):
        return self.graph.query(keys=node_names, live=True)
